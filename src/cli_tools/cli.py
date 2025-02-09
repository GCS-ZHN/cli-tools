import click

from cli_tools.core import CliManager
from dataclasses import dataclass


@dataclass
class GroupOption(object):
    manager: CliManager
    verbose: bool = False


@click.group()
@click.pass_context
def main(ctx: click.Context):
    ctx.obj = GroupOption(
        manager=CliManager()
    )


@main.command()
@click.argument('cli_name')
@click.option(
    '--cli_version',
    type=click.STRING,
    help='Specify the version of cli')
@click.option(
    '--force', '-f',
    is_flag=True,
    help='Force reinstall existed cli')
@click.pass_context
def install(ctx: click.Context, cli_name: str, cli_version: str = None, force: bool = False):
    """
    Install a specific CLI command.

    This command installs a CLI command specified by its name. Optionally, a version can be specified.
    If the command is already installed, it can be reinstalled by using the force option.
    """
    manager: CliManager = ctx.obj.manager
    try:
        manager.install_cli(cli_name, version=cli_version, force=force)
    except Exception as e:
        print(e)


@main.command()
@click.argument('cli_name', required=False)
@click.pass_context
def list(ctx: click.Context, cli_name: str = None):
    """
    List available CLI commands or details of a specific command.

    This command lists all available CLI commands if no specific command name is provided.
    If a command name is provided, it displays detailed information about that command,
    including its name, author, description, latest version, and available versions.
    """
    from prettytable import PrettyTable
    manager: CliManager = ctx.obj.manager
    if cli_name:
        cli_meta = manager.get_cli_meta(cli_name)
        authors = ', '.join(f"{a['name']} <{a['email']}>" for a in cli_meta.authors)
        print('Name       :', cli_meta.name)
        print('Authors    :', authors)
        print('Description:', cli_meta.description)
        print('Latest     :', cli_meta.latest)
        table = PrettyTable(['version', 'commit_id'])
        for v in cli_meta.versions:
            table.add_row([v['version'], v['commit']])
        print(table)
    else:
        cli_metas = manager.get_registry()['commands']
        print(f'Total {len(cli_metas)} clis found.')
        table = PrettyTable(['name', 'description', 'latest version'])
        for c in cli_metas:
            table.add_row([c.name, c.description, c.latest])
        print(table)


@main.command()
@click.argument('cli_name')
@click.pass_context
def uninstall(ctx: click.Context, cli_name: str):
    """
    Uninstall a specific CLI command.

    This command uninstalls a CLI command specified by its name.
    """
    manager: CliManager = ctx.obj.manager
    try:
        manager.uninstall_cli(cli_name)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
