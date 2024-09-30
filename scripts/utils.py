# Utility function to load a GraphQL query or fragment from a file
import json
import os
import time
import pandas as pd
import requests

from graphql_queries import *

class UnfollowError(Exception):
    def __init__(self, message, stopProcess):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
            
        self.stopProcess = stopProcess
    
def request_access_token():
    FIREBASE_TOKEN_URL = os.getenv("FIREBASE_API_URL") + os.getenv("FIREBASE_API_KEY")
    FIREBASE_REFRESH_TOKEN = os.getenv("FIREBASE_REFRESH_TOKEN")

    payload = {
        "grantType": "refresh_token",
        "refreshToken": FIREBASE_REFRESH_TOKEN
    }

    response = requests.post(FIREBASE_TOKEN_URL, json=payload)
    response.raise_for_status()
    access_data = response.json()
    return access_data['access_token']

def phaver_graphql_api_request(query, variables, access_token):
    PHAVER_GRAPHQL_ENDPOINT = os.getenv("PHAVER_GRAPHQL_ENDPOINT")

    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "variables": variables
    }

    response = requests.post(
        PHAVER_GRAPHQL_ENDPOINT, 
        headers=headers, 
        json=payload
    )

    # Raise an exception for HTTP errors
    if response.status_code != 200:
        print(response.headers)
        response.raise_for_status()

    # Parse the JSON response
    data = response.json()

    # Check if the response contains any errors
    if 'errors' in data:
        raise Exception(data['errors'])
    
    time.sleep(1)
    return data

def addToClipBoard(text):
    command = 'echo ' + text.strip() + '| clip'
    os.system(command)

def save_to_json(data, filename):
    """Save the data to a JSON file"""
    # create the folder if it doesn't exist
    folder = os.path.dirname(filename)
    os.makedirs(folder, exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
        
def request_followings(profile_id, limit_per_request, offset, access_token):
    """Fetch a batch of followings from the API"""

    data = phaver_graphql_api_request(
        query = FRAGMENTS + FOLLOWINGS_QUERY, 
        variables = {
            "profileId": profile_id,
            "limit": limit_per_request,
            "offset": offset
        }, 
        access_token = access_token
    )

    # get the followings from the response
    followings = data['data']['followings']
    
    return followings

def request_points(profile_id, access_token):
    """Fetch the points for a profile from the API"""

    data = phaver_graphql_api_request(
        query = FRAGMENTS + POINTS_QUERY, 
        variables = {
            "profileId": profile_id
        }, 
        access_token = access_token
    )
   
    # get the points from the response
    points = data['data']['phaverPoints']['phaverPointsCurrent']
    
    return points

def get_all_points(followings, access_token):
    """Fetch all points by iterating over paginated results"""
    for following in followings:
        profile_id = following['followedProfile']['id']
        points = request_points(profile_id, access_token)
        following['followedProfile']['points'] = points
    return followings


def get_all_followings(profile_id, limit_per_request, max_followings_requested, access_token):
    """Fetch all followings by iterating over paginated results"""
    all_followings = []
    offset = 0
    
    while len(all_followings) < max_followings_requested:
        followings = request_followings(profile_id, limit_per_request, offset, access_token)
        
        # If no more followings, break the loop
        if not followings:
            break
        
        # Append the fetched followings to the list
        all_followings.extend(followings)
        
        # Increment the offset by the limit for pagination
        offset += limit_per_request
        
    return all_followings

# Function to flatten the JSON data
def flatten_followings(followings):
    """Flatten the followings JSON data into Pandas DataFrame"""

    flattened_data = []

    for item in followings:
        followed_profile = item['followedProfile']
       
        # Flatten the nested fields
        flattened_profile = {
            "id": followed_profile.get("id"),
            "username": followed_profile.get("username"),
            "profileCreatedAt": followed_profile.get("createdAt"),
            "followingDate": item.get("createdAt"),
            "followerCount": followed_profile.get("profileAggregates", {}).get("followerCount") if followed_profile.get("profileAggregates") else None,
            "followingCount": followed_profile.get("profileAggregates", {}).get("followingCount") if followed_profile.get("profileAggregates") else None,
            "points": followed_profile.get("points"),
            "credLevel": followed_profile.get("credLevel"),
            "badge": followed_profile.get("badge"),
            "phaverFrens": followed_profile.get("phaverFrens"),
            "verification": followed_profile.get("verification"),
            "verified": followed_profile.get("verified"),
            "isUserFollowing": followed_profile.get("isUserFollowing"),
            "lensProfile.lensHandle": followed_profile.get("lensProfile", {}).get("lensHandle") if followed_profile.get("lensProfile") else None,
            "lensProfile.isUserFollowing": followed_profile.get("lensProfile", {}).get("isUserFollowing") if followed_profile.get("lensProfile") else None,
            "farcasterProfile.name": followed_profile.get("farcasterProfile", {}).get("name") if followed_profile.get("farcasterProfile") else None,
            "farcasterProfile.isUserFollowing": followed_profile.get("farcasterProfile", {}).get("isUserFollowing") if followed_profile.get("farcasterProfile") else None
        }

        # Append flattened profile to the list
        flattened_data.append(flattened_profile)

    return pd.DataFrame(flattened_data)

def request_profile(profile_id, access_token):
    """Fetch the profile data from the API"""

    data = phaver_graphql_api_request(
        query = FRAGMENTS + PROFILE_QUERY, 
        variables = {
            "profileId": profile_id
        }, 
        access_token = access_token
    )

    profile = data['data']['profile']
    return profile

def request_quota(profile_id, access_token):
    """Fetch the quota data from the API"""

    data = phaver_graphql_api_request(
        query = FRAGMENTS + QUOTA_QUERY, 
        variables = {
            "accountId": profile_id
        }, 
        access_token = access_token
    )

    quota = data['data']['quota']
    return quota

def unfollow_user(profile_id, unfollowed_profile_id, network, access_token):
    if network not in ['phaver', 'lens', 'farcaster', 'all']:
        raise ValueError(f"Invalid network '{network}' : Must be either 'phaver', 'lens', 'farcaster', or 'all'")
    if network == 'all':
        networks = ['phaver', 'lens', 'farcaster']
    else:
        networks = [network]

    profile = request_profile(unfollowed_profile_id, access_token)

    if profile is None:
        raise ValueError(f"Profile not found")
    
    # check if the user is not already unfollowing the profile on Phaver
    if 'phaver' in networks and not profile.get('isUserFollowing', False):
        networks.remove('phaver')

    # check if the profile has a Lens account, and if the user is not already unfollowing the profile on Lens
    if 'lens' in networks and (not profile.get('lensProfile') or not profile['lensProfile'].get('isUserFollowing', False)):
        networks.remove('lens')

    # check if the profile has a Farcaster account, and if the user is not already unfollowing the profile on Farcaster
    if 'farcaster' in networks and (not profile.get('farcasterProfile') or not profile['farcasterProfile'].get('isUserFollowing', False)):
        networks.remove('farcaster')

    if len(networks) == 0:
        return

    for network in networks:
        data = phaver_graphql_api_request(
            query = FRAGMENTS + SET_FOLLOW_MUTATION, 
            variables = {
                "follow": False,
                "profileId": unfollowed_profile_id,
                "followType": network
            }, 
            access_token = access_token
        )

        if data['data']['setFollow']['status'] != 'ok':
            raise UnfollowError(f"Failed to unfollow user on {network}.\nResponse data : {json.dumps(data, indent=4)}\nProfile : {json.dumps(profile, indent=4)}", False)
    
    #Check that the profile is not being followed on any network
    profile = request_profile(unfollowed_profile_id, access_token)

    if profile.get('isUserFollowing', True):
        raise UnfollowError(f"Failed to unfollow user on Phaver.\nResponse data : {json.dumps(data, indent=4)}\nProfile : {json.dumps(profile, indent=4)}", False)
    if profile.get('lensProfile') and profile['lensProfile'].get('isUserFollowing', True):
        if not profile['lensProfile'].get('isFollowPending', False): # Lens takes some time to update the isUserFollowing field, so we need to check if the follow is pending. If it is, we can assume the unfollow was successful.
            quota = request_quota(profile_id, access_token)
            limit = min(quota['lensApiOnchain']['dailyAvailable'], quota['lensApiOnchain']['hourlyAvailable'])
            if limit <= 0:
                raise UnfollowError(f"Failed to unfollow user on Lens. Onchain Lens API limit reached.\nResponse data : {json.dumps(data, indent=4)}\nProfile : {json.dumps(profile, indent=4)}\nQuota : {json.dumps(quota, indent=4)}", True)
            else:
                raise UnfollowError(f"Failed to unfollow user on Lens. Unkown error.\nResponse data : {json.dumps(data, indent=4)}\nProfile : {json.dumps(profile, indent=4)}\nQuota : {json.dumps(quota, indent=4)}", False)
    if profile.get('farcasterProfile') and profile['farcasterProfile'].get('isUserFollowing', True):
        raise UnfollowError(f"Failed to unfollow user on Farcaster. Unkown error.\nResponse data : {json.dumps(data, indent=4)}\nProfile : {json.dumps(profile, indent=4)}", False)

