#!/usr/bin/env python3

import subprocess
import time
import json
import sys
from pathlib import Path
from datetime import datetime

class BootRestartTester:
    def __init__(self, boot_sh_path="boot.sh"):
        self.boot_sh_path = Path(boot_sh_path)
        self.log_file = Path("logs/boot_restart_test.log")
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def _log(self, message):
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
    def _test_notify_telegram(self):
        """
        Test notify_telegram function with mock/dummy.
        """
        self._log("Testing notify_telegram function...")
        
        mock_token = "MOCK_TOKEN"
        mock_chat_id = "MOCK_CHAT_ID"
        
        test_script = f"""
#!/bin/sh
TELEGRAM_BOT_TOKEN="{mock_token}"
TELEGRAM_CHAT_ID="{mock_chat_id}"

notify_telegram() {{
  text="$1"
  if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "MOCK: Would send to Telegram: $text"
  fi
}}

notify_telegram "Test message from boot_restart_test"
"""
        
        test_file = Path("tests/test_notify.sh")
        test_file.write_text(test_script, encoding='utf-8')
        test_file.chmod(0o755)
        
        result = subprocess.run(
            ['sh', str(test_file)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        expected = "MOCK: Would send to Telegram: Test message from boot_restart_test"
        success = expected in result.stdout
        
        self._log(f"notify_telegram test: {'PASS' if success else 'FAIL'}")
        if not success:
            self._log(f"Expected: {expected}")
            self._log(f"Got: {result.stdout}")
        
        return success
    
    def _test_restart_loop(self):
        """
        Test that the restart loop exists with 5-second sleep.
        """
        self._log("Testing restart loop structure...")
        
        content = self.boot_sh_path.read_text(encoding='utf-8')
        
        has_while_true = 'while true' in content
        has_sleep_5 = 'sleep 5' in content
        has_notify = 'notify_telegram' in content
        
        success = has_while_true and has_sleep_5 and has_notify
        
        self._log(f"restart_loop test: {'PASS' if success else 'FAIL'}")
        if not has_while_true:
            self._log("Missing: while true")
        if not has_sleep_5:
            self._log("Missing: sleep 5")
        if not has_notify:
            self._log("Missing: notify_telegram")
        
        return success
    
    def _test_timeout_scenario(self):
        """
        Dynamically test that boot.sh restarts after claude exits.
        Uses a mock claude command that exits immediately.
        """
        self._log("Testing timeout scenario (dynamic)...")
        
        boot_sh_path = Path("tests/test_boot_copy.sh")
        
        boot_content = self.boot_sh_path.read_text(encoding='utf-8')
        
        mock_boot_content = boot_content.replace(
            'claude --dangerously-skip-permissions --channels plugin:telegram@claude-plugins-official -c',
            'exit 1'
        )
        
        boot_sh_path.write_text(mock_boot_content, encoding='utf-8')
        boot_sh_path.chmod(0o755)
        
        start_time = time.time()
        
        result = subprocess.run(
            ['sh', str(boot_sh_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=15
        )
        
        elapsed = time.time() - start_time
        
        expected_messages = [
            "boot.sh起動: ナナエビちゃんを起動します",
            "ナナエビちゃんが終了 → 5秒後に再起動します",
            "ナナエビちゃんを再起動します",
        ]
        
        has_messages = all(msg in result.stdout for msg in expected_messages)
        
        expected_min_time = 5
        expected_max_time = 12
        
        timing_ok = expected_min_time <= elapsed <= expected_max_time
        
        success = has_messages and timing_ok
        
        self._log(f"timeout_scenario test: {'PASS' if success else 'FAIL'}")
        if not has_messages:
            self._log(f"Expected messages: {expected_messages}")
            self._log(f"Got: {result.stdout}")
        if not timing_ok:
            self._log(f"Timing: elapsed={elapsed:.2f}s, expected {expected_min_time}-{expected_max_time}s")
        
        return success
    
    def run_all_tests(self):
        self._log("=" * 50)
        self._log("Starting boot restart tests")
        self._log("=" * 50)
        
        tests = [
            ("notify_telegram function", self._test_notify_telegram),
            ("restart loop structure", self._test_restart_loop),
            ("timeout scenario", self._test_timeout_scenario),
        ]
        
        results = {}
        for name, test_func in tests:
            print(f"Running {name}...", end=" ")
            result = test_func()
            status = "PASS" if result else "FAIL"
            print(status)
            results[name] = result
        
        print("-" * 50)
        
        all_passed = all(results.values())
        print(f"Overall: {'PASS' if all_passed else 'FAIL'}")
        
        self._log("=" * 50)
        self._log(f"Test results: {results}")
        self._log(f"Overall: {'PASS' if all_passed else 'FAIL'}")
        self._log("=" * 50)
        
        return all_passed

if __name__ == "__main__":
    tester = BootRestartTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)