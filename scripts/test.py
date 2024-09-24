from pathlib import Path
project_dir = Path(__file__).resolve().parents[1]

Fragments_file = project_dir / 'graphql/fragments/Fragments.gql'
print(Fragments_file)