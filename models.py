from dataclasses import dataclass


@dataclass()
class Repository:
    owner: str
    name: str
    
    def __init__(self, **kwargs):
        self.owner = kwargs['owner']['login']
        self.name = kwargs['name']


@dataclass()
class Author:
    name: str
    email: str

    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.email = kwargs['email']


@dataclass()
class Commit:
    repository: Repository
    author: Author
    message: str
    sha: str

    def __init__(self, repository: Repository, **kwargs):
        self.sha = kwargs['sha']
        self.repository = repository
        self.author = Author(**kwargs['commit']['author'])
        self.message = kwargs['commit']['message']
