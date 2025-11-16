from enum import Enum
from datetime import datetime
import os


class ExecutionModes(Enum):
    ASSERT = "test"
    REPORT = "report"
    SET_REFERENCE = "set-reference"
    SET_BASELINE = "set-baseline"

class DefaultThresholds():
    claim_check = 0.90
    general_criteria = 0.90

_initial_mode = ExecutionModes.ASSERT
_aim_mode_env = os.getenv("AIM_MODE")
if _aim_mode_env:
    _initial_mode = ExecutionModes(_aim_mode_env)


class ExecutionMode:
    mode = _initial_mode
    iteration = int(os.getenv("AIM_ITERATION", "0"))
    config = None
    default_thresholds = DefaultThresholds()
    failures_dir = "aim_data/failures"
    report_dir = "aim_data/report"
    reference_dir = "aim_data/reference"
    _timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    failures_file = f"{failures_dir}/failures_{_timestamp}.json"
    report_file = f"{report_dir}/report_{_timestamp}.json"


def set_mode(mode: ExecutionModes, iteration=None, config=None):
    ExecutionMode.mode = mode
    ExecutionMode.iteration = iteration
    ExecutionMode.config = config
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    ExecutionMode.failures_file = f"{ExecutionMode.failures_dir}/failures_{timestamp}.json"
    ExecutionMode.report_file = f"{ExecutionMode.report_dir}/report_{timestamp}.json"

def get_base_thresholds():
    return ExecutionMode.default_thresholds

def get_mode() -> ExecutionModes:
    return ExecutionMode.mode