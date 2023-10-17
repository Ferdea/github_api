from constants import BASE_URL, TOKEN
from aiohttp import ClientSession
from models import Repository, Branch, Commit
from re import compile


HEADERS: dict = {'Authorization': f'Bearer {TOKEN}'}
next_link_regexp = compile(r'<([^>]+)>;\srel="next"')


async def _get_organization_repositories(session: ClientSession, organization: str) -> list[Repository]:
    url = f'{BASE_URL}/orgs/{organization}/repos'

    async with session.get(url, headers=HEADERS) as response:
        repositories_json = await response.json()
        repositories = [Repository(**repository_json) for repository_json in repositories_json]

    return repositories


async def get_organization_repositories(organization: str) -> list[Repository]:
    async with ClientSession() as session:
        repositories = await _get_organization_repositories(session, organization)
    
    return repositories


async def _get_repository_branches(session: ClientSession, repository: Repository) -> list[Branch]:
    url = f'{BASE_URL}/repos/{repository.owner}/{repository.name}/branches'
    
    async with session.get(url, headers=HEADERS) as response:
        branches_json = await response.json()
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
        async with session.get(url, headers=HEADERS) as response:
            commits_json = await response.json()
            commits += [Commit(branch=branch, **commit_json) for commit_json in commits_json]
            
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


async def get_organization_commits(organization: str) -> list[Commit]:
    result_commits = set()
    
    async with ClientSession() as session:
        repositories = await _get_organization_repositories(session, organization)
            
        for repository in repositories:
            branches = await _get_repository_branches(session, repository)
            
            for branch in branches:
                commits = await _get_branch_commits(session, branch)                        
                result_commits = result_commits.union(commits)
            
    return result_commits
