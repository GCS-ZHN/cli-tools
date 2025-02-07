
import sys
import subprocess

from pathlib import Path

PROJECT_DIR = Path(__file__).parent


def install_script(name: str):
    script_path = PROJECT_DIR / f"cli_{name}.py"
    target_path = Path.home() / ".local" / "bin" / name
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, 'w') as target_file:
        target_file.write(f"#!{sys.executable}\n")
        with open(script_path, 'r') as source_file:
            for line in source_file:
                if line.strip().startswith("#"):
                    continue

                target_file.write(line)
    target_path.chmod(0o755)
    print(f"Installed {name} command to {target_path}")


def install_deps(name: str):
    requirements = PROJECT_DIR / f"requirements_{name}.txt"
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements)])


if len(sys.argv) > 1:
    if sys.argv[1] == "install":
        cli_names = sys.argv[2:]
        if cli_names:
            name_iter = cli_names
        else:
            name_iter = map(lambda x: x.name[4:-3], PROJECT_DIR.glob("cli_*.py"))
        for name in name_iter:
            install_script(name)
            install_deps(name)
