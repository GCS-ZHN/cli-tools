import requests
import subprocess
from dataclasses import dataclass
from typing import Dict, List

REGISTRY_URL = "https://raw.githubusercontent.com/{repo}/refs/heads/{commit}/registry.yaml"
REGISTRY_REPO = "git+https://github.com/{repo}.git@{commit}#subdirectory={path}"

@dataclass
class CliMeta:
    name: str
    description: str
    path: str
    authors: List[Dict[str, str]]
    latest: str
    versions: List[Dict[str, str]]


class VersionedManager:
    def __init__(self, repo: str = "GCS-ZHN/cli-tools-registry"):
        self.repo = repo
        self.registry_cache = {}

    def get_registry(self, commit: str = "main") -> Dict:
        """获取指定commit的注册表"""
        if commit in self.registry_cache:
            return self.registry_cache[commit]
            
        url = REGISTRY_URL.format(repo=self.repo, commit=commit)
        response = requests.get(url)
        response.raise_for_status()
        
        import yaml  # 需添加PyYAML依赖
        registry = yaml.safe_load(response.text)
        registry['commands'] = [CliMeta(**c) for c in registry['commands']]
        self.registry_cache[commit] = registry
        return registry

    def install_cli(self, cli_name: str, version: str = None, force: bool = False):
        """
        Install a specific version of a command.

        This method installs a command specified by its name and version. If the version is not provided,
        the latest version will be installed. If the command is already installed, it can be reinstalled
        by using the force option.

        Args:
            cli_name (str): The name of the command to install.
            version (str, optional): The version of the command to install. Defaults to None.
            force (bool, optional): If True, forces reinstallation of the command if it already exists. Defaults to False.

        Raises:
            ValueError: If the command or the specified version is not found in the registry.
        """
        cli_meta = self.get_cli_meta(cli_name)
        target_version = version or cli_meta.latest
        for version_info in cli_meta.versions:
            if version_info['version'] == target_version:
                break
        else:
            raise ValueError(f'Invalid version "{target_version}", see available version at "ctl list {cli_name}"')
        
        install_url = REGISTRY_REPO.format(
            repo=self.repo,
            commit=version_info['commit'],
            path=cli_meta.path
            )
        args = ["pipx", "install", install_url]
        if force:
            args.append('--force')
        result = subprocess.run(args)
        if result.returncode != 0:
            raise RuntimeError(f'Install cli {cli_name} failed.')

    def uninstall_cli(self, cli_name: str):
        """
        Uninstall a specific command.

        This method uninstalls a command specified by its name.

        Args:
            cli_name (str): The name of the command to uninstall.

        Raises:
            ValueError: If the command is not found in the registry.
        """
        self.get_cli_meta(cli_name)
        args = ["pipx", "uninstall", 'cli-' + cli_name]
        result = subprocess.run(args)
        if result.returncode != 0:
            raise RuntimeError(f'Uninstall cli {cli_name} failed.')

    def get_cli_meta(self, cli_name: str) -> CliMeta:
        """
        Retrieve the metadata for a specific CLI command.

        This method fetches the metadata for a given CLI command by its name from the registry.
        The metadata includes information such as the command's name, author, description, latest version,
        and available versions.

        Args:
            cli_name (str): The name of the CLI command to retrieve metadata for.

        Returns:
            CliMeta: An object containing the metadata of the specified CLI command.

        Raises:
            ValueError: If the CLI command is not found in the registry.
        """
        registry = self.get_registry()
        for cli_meta in registry['commands']:
            if cli_meta.name == cli_name:
                break
        else:
            raise ValueError(f'Cli "{cli_name}" not found, see available cli at "ctl list"')

        return cli_meta

