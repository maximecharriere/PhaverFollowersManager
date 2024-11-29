## Script to unfollow profiles on a daily basis until my followings list is cleaned up.
## Each days, if the lens quotas is reached, the script will stop and continue the next day.
## The script must be run with a cron job to unfollow profiles on a daily basis.

import pandas as pd
import os
from dotenv import load_dotenv
from utils import *
from pathlib import Path

load_dotenv()

project_dir = Path(__file__).resolve().parents[1]

####################
# Request Access Token
####################
print("Request Access Token")
print("-------------------------")
access_token = request_access_token()
print("Access Token: Bearer ", access_token)

####################
# Load Followings Dataframe
####################
print("\nLoad Followings Dataframe")
print("-------------------------")
followings_df = pd.read_csv(project_dir / 'data/followings.csv')
print(f"Loaded {len(followings_df)} followings.")

####################
# Filter profiles to unfollow
####################
print("\nFilter profiles to unfollow")
print("-------------------------")
profiles_to_unfollow_df = followings_df[
    (followings_df['followerCount'] < 3000) & 
    (followings_df['credLevel'] < 3) &
    (followings_df['badge'].isnull()) &
    (followings_df['verification'].isnull()) &
    # (followings_df['lensProfile.isUserFollowing'] != True) &
    (followings_df['tempo_unfollowed'] == False) 
]
print(f"Found {len(profiles_to_unfollow_df)} profiles to unfollow.")

####################
# Unfollow profiles
####################
error_count = 0
error_limit = 5

try:
    # Unfollow Profiles
    for index, following in profiles_to_unfollow_df.head(120).iterrows():
        try:
            unfollow_user(os.getenv("PHAVER_PROFILE_ID"), following['id'], 'all', access_token)
        except ValueError as e:
            print(f"{e.__class__.__name__} on Profile `{following['username']}` : {e}")
            if error_count >= error_limit:
                break
            else:
                error_count+=1
                continue
        except UnfollowError as e:
            print(f"{e.__class__.__name__} on Profile `{following['username']}` : {e}")
            if e.stopProcess:
                break
            else : 
                if error_count >= error_limit:
                    break
                else:
                    error_count+=1
                    continue
        print(f"Unfollowed {following['username']}")
        followings_df.loc[index, 'tempo_unfollowed'] = True
finally:
    # Save modified following list
    followings_df.to_csv(project_dir / 'data/followings.csv', index=False)
    print("Saved followings list.")
