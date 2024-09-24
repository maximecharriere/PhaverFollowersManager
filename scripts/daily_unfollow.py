import pandas as pd
import os
from dotenv import load_dotenv
from utils import *
from pathlib import Path

load_dotenv()

project_dir = Path(__file__).resolve().parents[1]

####################
# Request Token
####################

access_token = request_access_token()
print("Access Token: Bearer ", access_token)

####################
# Load Followings Dataframe
####################

followings_df = pd.read_csv(project_dir / 'data/followings.csv')
print(f"Loaded {len(followings_df)} followings.")

####################
# Filter profiles to unfollow
####################

profiles_to_unfollow_df = followings_df[
    (followings_df['followerCount'] < 2000) & 
    (followings_df['credLevel'] < 2) &
    (followings_df['badge'].isnull()) &
    (followings_df['verification'].isnull()) &
    # (followings_df['lensProfile.isUserFollowing'] != True) &
    (followings_df['tempo_unfollowed'] == False) 
]
print(f"Found {len(profiles_to_unfollow_df)} profiles to unfollow.")

####################
# Unfollow profiles
####################

try:
    # Unfollow Profiles
    for index, following in profiles_to_unfollow_df.head(5).iterrows():
        unfollowed = unfollow_user(os.getenv("PHAVER_PROFILE_ID"), following['id'], 'all', access_token)
        if unfollowed:
            print(f"Unfollowed {following['username']}")
            followings_df.loc[index, 'tempo_unfollowed'] = True
finally:
    # Save modified following list
    followings_df.to_csv(project_dir / 'data/followings.csv', index=False)
    print("Saved followings list.")
