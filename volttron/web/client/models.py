from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import List, Dict, Optional, Tuple, Any

from volttron.web.client.base import Http, AuthenticationError

_log = logging.getLogger(__name__)

LINK_IDENTIFIER = 'links'


class InvalidPlatformReference(Exception):
    pass


class InvalidAgentReference(Exception):
    pass

class InvalidRPCFunction(Exception):
    pass


@dataclass
class Link:
    key: str
    link: str


@dataclass
class Platform(Http):
    name: str
    links: List[Link] = field(default_factory=list)

    @property
    def agents(self) -> List[Agent]:
        agent_list: List[Agent] = []
        for link in self.links:
            if 'agents' == link.key:
                response = self.get(link.link, params={"agent-state": "installed"})
                if response.ok:
                    links = build_links(response.json()[LINK_IDENTIFIER])
                    for link in links:
                        agent_list.append(Agent(platform=self.name, identity=link.key, link=link.link,
                                                links=links))
                    break
        return agent_list

    @property
    def status(self) -> List[AgentStatus]:
        status = None
        contexts: List[AgentStatus] = []
        for link in self.links:
            if 'status' == link.key:
                status = self.get(link.link)
                for k, v in status.json().items():
                    contexts.append(AgentStatus(identity=k,
                                                name=v['name'],
                                                platform=self.name,
                                                exit_code=v['exit_code'],
                                                priority=v['priority'],
                                                running=v['running'],
                                                enabled=v['enabled'],
                                                tag=v['tag'],
                                                uuid=v['uuid']))
        return status.json()

    def get_agent(self, identity: str) -> Agent:
        response = self.get(f"/vui/platforms/{self.name}/agents/{identity}")
        agent: Optional[Agent] = None
        if response.ok:
            links = build_links(response.json()[LINK_IDENTIFIER])
            agent = Agent(self.name, identity=identity, link=f"/vui/platforms/{self.name}/agents/{identity}",
                          links=links)
        else:
            raise InvalidAgentReference()
        return agent


def build_links(kv: Dict[str, str]) -> List[Link]:
    links: List[Link] = []
    for k, v in kv.items():
        links.append(Link(k, v))
    return links


class Platforms(Http):

    def __init__(self):
        if not self.__auth__:
            raise AuthenticationError("Authenticate before accessing platforms.")

    def list(self) -> List[Platform]:
        response = self.get("/vui/platforms")
        platforms: List[Platform] = []
        if response.ok:
            # a link of platforms with key = platform name and
            # link a link to the specific platform
            pforms = build_links(response.json()[LINK_IDENTIFIER])
            for l in pforms:
                response = self.get(l.link)
                if response.ok:
                    l2 = build_links(response.json()[LINK_IDENTIFIER])
                    platforms.append(Platform(l.key, l2))
        return platforms

    def get_platform(self, name: str) -> Platform:
        response = super().get(f"/vui/platforms/{name}")
        platform: Optional[Platform] = None
        if response.ok:
            links = build_links(response.json()[LINK_IDENTIFIER])
            platform = Platform(name=name, links=links)
        else:
            raise InvalidPlatformReference()

        return platform


@dataclass
class Agent(Http):
    platform: str
    identity: str
    link: str
    links: List[Link]

    @property
    def configs(self) -> AgentConfigs:
        response = self.get(url=f'{self.link}/configs')
        links = build_links(response.json()[LINK_IDENTIFIER])
        configs = AgentConfigs(identity=self.identity, link=f'{self.link}/configs', links=links)
        return configs

    @property
    def enabled(self) -> AgentEnabled:
        response = self.get(url=f'{self.link}/enabled')
        status = response.json()['status']
        priority = response.json()['priority']
        return AgentEnabled(enabled=bool(status), priority=priority)

    @property
    def status(self) -> AgentStatus:
        response = self.get(url=f"{self.link}/status")
        obj = response.json()
        context = AgentStatus(name=obj['name'],
                              identity=self.identity,
                              platform=self.platform,
                              exit_code=obj['exit_code'],
                              priority=obj['priority'],
                              running=obj['running'],
                              enabled=obj['enabled'],
                              tag=obj['tag'],
                              uuid=obj['uuid'])
        return context

    @property
    def rpc(self) -> AgentRPC:
        response = self.get(url=f'{self.link}/rpc')
        rpc: Optional[AgentRPC] = None
        if response.ok:
            links = build_links(response.json()[LINK_IDENTIFIER])
            rpc = AgentRPC(links)
        return rpc

    @property
    def running(self) -> bool:
        response = self.get(url=f'{self.link}/running')
        return response.json()['running']


@dataclass
class AgentStatus:
    name: str
    identity: str
    platform: str
    uuid: str
    running: bool
    enabled: bool
    pid: Optional[str] = None
    tag: Optional[str] = ''
    exit_code: Optional[str] = None
    priority: Optional[int] = None


class Historian:
    pass


class Driver:
    pass


def cbool(data: str) -> bool:
    if data.lower() == 'true':
        status = True
    elif data.lower() == 'false':
        status = False
    else:
        status = False
    return status


def get_link(key: str, links: List[Link]) -> Link:
    for link in links:
        if link.key == key:
            return link
    return None


@dataclass
class AgentConfigs(Http):
    identity: str
    link: str
    links: List[Link]

    def __get_link__(self, key) -> Optional[Link]:
        for link in self.links:
            if link.key == key:
                return link
        return None

    @property
    def entries(self) -> List[ConfigStoreEntry]:
        entry_list: List[ConfigStoreEntry] = []
        for link in self.links:
            response = self.get(link.link)
            if response.ok:
                key = link.link.replace(f'{self.link}/', '')
                entry_list.append(ConfigStoreEntry(link=link.link, key=key, content=response.json(),
                                                   content_type=response.headers.get('Content-Type')))
        return entry_list


@dataclass
class ConfigStoreEntry(Http):
    link: str
    key: str
    content: Optional[str] = None
    content_type: Optional[str] = None

    def update(self, new_entry):
        self.put(self.link, data=new_entry)


@dataclass
class AgentEnabled(Http):
    link: str
    enabled: bool
    priority: Optional[int] = 0

    def update_enabled(self, enabled: bool, priority: int = 50):
        if enabled:
            response = self.put(self.link, params={'priority': priority})
        else:
            response = self.delete(self.enabled.link)

    def update_priority(self, priority: int):
        self.update_enabled(True, priority)


@dataclass
class AgentRPC(Http):
    links: List[Link]

    def execute(self, function_name: str, **kwargs) -> RPCResponse:
        link = get_link(function_name, self.links)
        if link is None:
            raise InvalidRPCFunction(f"{function_name} does not exist")

        body = {}
        for k, v in kwargs.items():
            body[k] = v
        response = self.post(url=link.link, json=body)

        rpc_repsonse: Optional[RPCResponse] = None
        if response.ok:
            rpc_repsonse = RPCResponse(data=response.json())

        return rpc_repsonse


@dataclass
class RPCResponse:
    data: Any
    error: Optional[bool] = False
