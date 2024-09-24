from pathlib import Path

def load_graphql_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

project_dir = Path(__file__).resolve().parents[1]

FRAGMENTS = load_graphql_file(project_dir / 'graphql/fragments/Fragments.gql')
FOLLOWINGS_QUERY = load_graphql_file(project_dir / 'graphql/queries/FollowingsQuery.gql')
FOLLOWERS_QUERY = load_graphql_file(project_dir / 'graphql/queries/FollowersQuery.gql')
POINTS_QUERY = load_graphql_file(project_dir / 'graphql/queries/PointsQuery.gql')
SET_FOLLOW_MUTATION = load_graphql_file(project_dir / 'graphql/mutations/SetFollowMutation.gql')
PROFILE_QUERY = load_graphql_file(project_dir / 'graphql/queries/ProfileQuery.gql')
QUOTA_QUERY = load_graphql_file(project_dir / 'graphql/queries/QuotaQuery.gql')