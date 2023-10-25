from collections import Counter
from constants import ORGANIZATION
from models import Commit
from asyncio import run
from github_api_methods import get_organization_commits
from time import time


def ignore_merge_request(commit: Commit):
    return not commit.message.startswith('Merge pull request #')


async def main():
    start = time()
    
    counter = Counter()
    commits = await get_organization_commits(ORGANIZATION)
    for commit in filter(ignore_merge_request, commits):
        counter[commit.author.email] += 1
        print(commit.message)
            
    print(f'Прошедшее время: {time() - start}')
    print(f'Вот топ-{min(100, len(counter))}')
    for index, email in enumerate(sorted(counter.keys(), key=counter.get, reverse=True)[:100]):
        print(f'{index + 1}. {email} : {counter[email]}')  
    
    
run(main())
