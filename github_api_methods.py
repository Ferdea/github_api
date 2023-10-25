from constants import BASE_URL, TOKEN
from aiohttp import ClientSession
from models import Repository, Branch, Commit
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


async def _get_repository_branches(session: ClientSession, repository: Repository) -> list[Branch]:
    url = f'{BASE_URL}/repos/{repository.owner}/{repository.name}/branches'
    
    response = await get(session, url, headers=HEADERS)
    branches_json = response.json
    branches = [Branch(repository=repository, **branch_json) for branch_json in branches_json]
    
    return branches


async def get_repository_branches(repository: Repository) -> list[Branch]:
    async with ClientSession() as session:
        branches = await _get_repository_branches(session, repository)

    return branches
    

async def _get_branch_commits(session: ClientSession, branch: Branch) -> list[Commit]:
    url = f'{BASE_URL}/repos/{branch.repository.owner}/{branch.repository.name}/commits?per_page=100&sha={branch.last_commit_sha}'
    commits = []
    
    while True:
        response = await get(session, url, headers=HEADERS)
        commits_json = response.json
        commits += [Commit(branch=branch, repository=branch.repository, **commit_json) for commit_json in commits_json]

        if 'Link' not in response.headers:
            break

        next_url_result = next_link_regexp.findall(response.headers['Link'])

        if len(next_url_result) == 0:
            break

        url = next_url_result[0]
                
    return commits


async def get_branch_commits(branch: Branch) -> list[Commit]:
    async with ClientSession() as session:
        commits = await _get_branch_commits(session, branch)
    
    return commits


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


async def get_organization_commits(organization: str) -> list[Commit]:
    async with ClientSession() as session:
        repositories = await _get_organization_repositories(session, organization)

        async def get_repository_commits_async(repository: Repository) -> list[Commit]:
            return await _get_repository_commits(session, repository)

        tasks = (get_repository_commits_async(repository) for repository in repositories)
        commit_parts = await gather(*tasks)

    result_commits = []
    for commit_part in commit_parts:
        result_commits += commit_part

    print(len(repositories), result_commits)
    return result_commits
