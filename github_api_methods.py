from constants import BASE_URL, TOKEN
from aiohttp import ClientSession
from models import Repository, Commit
from re import compile
from asyncio import gather
from request_limiter import get


HEADERS: dict = {'Authorization': f'Bearer {TOKEN}'}
next_link_regexp = compile(r'<([^>]+)>;\srel="next"')


async def _get_organization_repositories(session: ClientSession, organization: str) -> list[Repository]:
    url = f'{BASE_URL}/orgs/{organization}/repos'

    response = await get(session, url, headers=HEADERS)
    repositories_json = response.json
    repositories = [Repository(**repository_json) for repository_json in repositories_json]

    return repositories


async def get_organization_repositories(organization: str) -> list[Repository]:
    async with ClientSession() as session:
        repositories = await _get_organization_repositories(session, organization)
    
    return repositories


async def _get_repository_commits(session: ClientSession, repository: Repository) -> list[Commit]:
    url = f'{BASE_URL}/repos/{repository.owner}/{repository.name}/commits'
    commits = []

    while True:
        response = await get(session, url, headers=HEADERS)
        commits_json = response.json
        commits += [Commit(repository=repository, **commit_json) for commit_json in commits_json]

        if 'Link' not in response.headers:
            break

        next_url_result = next_link_regexp.findall(response.headers['Link'])

        if len(next_url_result) == 0:
            break

        url = next_url_result[0]

    return commits


async def get_repository_commits(repository: Repository) -> list[Commit]:
    async with ClientSession() as session:
        return await _get_repository_commits(session, repository)


async def get_organization_commits(organization: str) -> list[Commit]:
    async with ClientSession() as session:
        repositories = await _get_organization_repositories(session, organization)

        tasks = (_get_repository_commits(session, repository) for repository in repositories)
        commit_parts = await gather(*tasks)

    result_commits = []
    for commit_part in commit_parts:
        result_commits += commit_part

    return result_commits
