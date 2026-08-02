from src.github_client.url_parser import parse_repo_url


def test_parse_repo_url() -> None:
    owner, name = parse_repo_url("https://github.com/owner/repo")
    assert owner == "owner"
    assert name == "repo"
