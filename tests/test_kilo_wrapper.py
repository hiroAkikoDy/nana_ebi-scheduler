#!/usr/bin/env python3

import unittest
import subprocess
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import kilo_wrapper

class TestKiloWrapper(unittest.TestCase):
    def setUp(self):
        self.test_log = Path("logs/test_kilo_wrapper.log")
        self.wrapper = kilo_wrapper.KiloWrapper(timeout_seconds=10, log_file=str(self.test_log))
        
    def test_execute_kilo_task_timeout(self):
        """
        Test that timeout is correctly detected.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('kilo', 10)
            result = self.wrapper.execute_kilo_task("test task")
            
            self.assertEqual(result["status"], "timeout")
            self.assertIn("timed out", result["error"])
    
    def test_execute_kilo_task_success(self):
        """
        Test that success is correctly detected.
        """
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "Task completed successfully"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            result = self.wrapper.execute_kilo_task("test task")
            
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["output"], "Task completed successfully")
    
    def test_execute_kilo_task_failure(self):
        """
        Test that failure is correctly detected.
        """
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Task failed"
            mock_run.return_value = mock_result
            
            result = self.wrapper.execute_kilo_task("test task")
            
            self.assertEqual(result["status"], "failure")
            self.assertEqual(result["error"], "Task failed")
    
    def test_execute_kilo_task_not_found(self):
        """
        Test that FileNotFoundError is correctly handled.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = self.wrapper.execute_kilo_task("test task")
            
            self.assertEqual(result["status"], "error")
            self.assertIn("not found", result["error"])
    
    def test_log_file_created(self):
        """
        Test that log file is created and appended.
        """
        test_message = "Test log message"
        self.wrapper._log(test_message)
        
        self.assertTrue(self.test_log.exists())
        log_content = self.test_log.read_text(encoding='utf-8')
        self.assertIn(test_message, log_content)

if __name__ == "__main__":
    unittest.main()