from src.github_client.repository_loader import RepositoryLoader


def test_load_local_path() -> None:
    loader = RepositoryLoader()
    repo = loader.load(".")
    assert repo.name == "."
