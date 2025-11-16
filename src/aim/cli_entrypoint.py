import json
import os
from pathlib import Path
import subprocess
from .cli_args import build_parser
from .state import set_mode, ExecutionModes

def load_config(path: str) -> dict:
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
    
def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cmd = args.command
    aim_config = load_config(args.config)
    
    mode = ExecutionModes(cmd)
    iteration = getattr(args, 'runs', None)
    
    set_mode(mode, iteration=iteration, config=aim_config)
    
    env = os.environ.copy()
    env["AIM_MODE"] = cmd
    if iteration:
        env["AIM_ITERATION"] = str(iteration)

    # For baseline mode, run multiple times
    if mode == ExecutionModes.SET_BASELINE and iteration:
        for i in range(iteration):
            print(f"Running iteration {i+1}/{iteration}...")
            subprocess.run(aim_config["run"], shell=True, check=False, env=env)
    else:
        subprocess.run(aim_config["run"], shell=True, check=False, env=env)
