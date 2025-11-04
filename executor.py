from __future__ import annotations

from typing import Type

from classe import ssh
from commands import RemoteCommand


class RemoteExecutor:
    def __init__(self, client: ssh):
        self.client = client

    def run(self, command: RemoteCommand) -> object:
        raw_output = self.client.execute(command.build())
        return command.parse(raw_output)


class SSHSessionFactory:
    def __init__(self, hostname: str, username: str, password: str):
        self.hostname = hostname
        self.username = username
        self.password = password

    def create(self) -> ssh:
        client = ssh(self.hostname, self.username, self.password)
        client.connect()
        return client


class CommandRunner:
    def __init__(self, session_factory: SSHSessionFactory):
        self.session_factory = session_factory

    def execute(self, command: RemoteCommand) -> object:
        client = self.session_factory.create()
        try:
            executor = RemoteExecutor(client)
            return executor.run(command)
        finally:
            client.close_connection()

    def execute_many(self, *commands: RemoteCommand) -> list[object]:
        results = []
        for command in commands:
            results.append(self.execute(command))
        return results
