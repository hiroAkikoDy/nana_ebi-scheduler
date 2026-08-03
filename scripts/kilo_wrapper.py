#!/usr/bin/env python3

import subprocess
import json
import sys
import os
import signal
from pathlib import Path
from datetime import datetime

class KiloWrapper:
    def __init__(self, timeout_seconds=300, log_file="logs/kilo_wrapper.log"):
        self.timeout_seconds = timeout_seconds
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _log(self, message):
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
    def execute_kilo_task(self, task_prompt):
        """
        Execute kilo run --auto with timeout.
        Returns JSON with status, output, error.
        """
        self._log(f"Starting task: {task_prompt[:50]}...")
        
        try:
            result = subprocess.run(
                ['kilo', 'run', '--auto', task_prompt],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                encoding='utf-8',
                errors='replace'
            )
            
            status = "success" if result.returncode == 0 else "failure"
            self._log(f"Task completed with status: {status}")
            
            return {
                "status": status,
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            self._log(f"Task timed out after {self.timeout_seconds} seconds")
            return {
                "status": "timeout",
                "output": "",
                "error": f"Task timed out after {self.timeout_seconds} seconds",
                "return_code": None
            }
        except FileNotFoundError:
            self._log("kilo command not found")
            return {
                "status": "error",
                "output": "",
                "error": "kilo command not found. Please install Kilo Code CLI.",
                "return_code": None
            }
        except Exception as e:
            self._log(f"Unexpected error: {str(e)}")
            return {
                "status": "error",
                "output": "",
                "error": str(e),
                "return_code": None
            }
    
    def execute_task(self, task_prompt):
        """
        Main entry point.
        """
        result = self.execute_kilo_task(task_prompt)
        return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python kilo_wrapper.py '<task_prompt>' [timeout_seconds]")
        sys.exit(1)
    
    task_prompt = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    
    wrapper = KiloWrapper(timeout_seconds=timeout)
    result = wrapper.execute_task(task_prompt)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "success" else 1)