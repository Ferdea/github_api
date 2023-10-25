from asyncio import sleep
from aiohttp import ClientSession, ClientResponse
from time import time
from yarl import URL
from dataclasses import dataclass
from typing import Any
from multidict import MultiDict
from typing import Callable, Awaitable, ParamSpecKwargs


@dataclass
class Response:
    status: int
    json: Any
    headers:  dict[str, Any]   


class Limiter:
    def __init__(self):
        self.last_request_time = time()
    
    def __call__(self, function: Callable[[ClientSession, str | URL, ParamSpecKwargs], Awaitable[ClientResponse]]):
        async def wrapper(*args, **kwargs):
            result = await function(*args, **kwargs)
            self.last_request_time = time()
            
            if result.status == 200:
                return result           
            
            if 'X-RateLimit-Reset' not in result.headers:
                print(result.headers)
            requests_reset = int(result.headers['X-RateLimit-Reset'])
            requests_remaining = int(result.headers['X-RateLimit-Remaining'])
            
            print(requests_reset - time())
            
            if requests_remaining == 0:
                await sleep(requests_reset - time())
            
            current_time = time()               
            if current_time - self.last_request_time < 0.75:
                await sleep(0.75 - current_time + self.last_request_time)
            
            result = await function(*args, **kwargs)
            result.raise_for_status()

            return result
            
        return wrapper


@Limiter()
async def get(session: ClientSession, url: str | URL, **kwargs) -> Response:
    async with session.get(url, **kwargs) as response:        
        return Response(response.status, await response.json(), dict(response.headers))
    