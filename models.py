from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class Repository:
    owner: str
    name: str
    
    def __init__(self, **kwargs):
        self.owner = kwargs['owner']['login']
        self.name = kwargs['name']


@dataclass(unsafe_hash=True)
class Branch:
    name: str
    last_commit_sha: str
    repository: Repository
    
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.last_commit_sha = kwargs['commit']['sha']
        self.repository = kwargs['repository']


@dataclass(unsafe_hash=True)
class Author:
    name: str
    email: str

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.email = kwargs['email']


@dataclass(unsafe_hash=True)
class Commit:
    branch: Branch | None
    repository: Repository
    author: Author
    message: str
    sha: str

    def __init__(self, repository: Repository, branch: Branch = None, **kwargs):
        self.sha = kwargs['sha']
        self.branch = branch
        self.repository = repository
        self.author = Author(**kwargs['commit']['author'])
        self.message = kwargs['commit']['message']
