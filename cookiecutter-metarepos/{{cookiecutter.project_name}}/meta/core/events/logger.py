"""
Event logging system for MetaRepos.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

from .schema import Event

logger = logging.getLogger(__name__)

class EventLogger:
    """Handles logging of events to a file with rotation."""
    
    def __init__(
        self,
        log_dir: Union[str, Path],
        max_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        self.log_dir = Path(log_dir)
        self.max_size = max_size
        self.backup_count = backup_count
        self.current_log_file: Optional[Path] = None
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the current log file
        self._init_log_file()
    
    def _init_log_file(self) -> None:
        """Initialize or rotate the log file if needed."""
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        self.current_log_file = self.log_dir / f"events-{current_date}.log"
        
        # Check if we need to rotate
        if self.current_log_file.exists() and self.current_log_file.stat().st_size > self.max_size:
            self._rotate_logs()
    
    def _rotate_logs(self) -> None:
        """Rotate log files, keeping only the specified number of backups."""
        if not self.current_log_file:
            return
        
        # Rename existing backup files
        for i in range(self.backup_count - 1, 0, -1):
            old_backup = self.current_log_file.with_suffix(f".{i}")
            new_backup = self.current_log_file.with_suffix(f".{i + 1}")
            
            if old_backup.exists():
                if i == self.backup_count - 1:
                    old_backup.unlink()
                else:
                    old_backup.rename(new_backup)
        
        # Rename current log file to .1
        if self.current_log_file.exists():
            self.current_log_file.rename(self.current_log_file.with_suffix(".1"))
    
    def log_event(self, event: Event) -> None:
        """Log an event to the current log file."""
        if not self.current_log_file:
            self._init_log_file()
        
        # Check if we need to rotate based on date
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        expected_log_file = self.log_dir / f"events-{current_date}.log"
        
        if expected_log_file != self.current_log_file:
            self.current_log_file = expected_log_file
        
        # Check if we need to rotate based on size
        if self.current_log_file.exists() and self.current_log_file.stat().st_size > self.max_size:
            self._rotate_logs()
        
        # Log the event
        try:
            with open(self.current_log_file, 'a') as f:
                event_data = event.to_dict()
                f.write(json.dumps(event_data) + '\n')
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
    
    def get_recent_events(self, count: int = 100) -> list[Dict]:
        """Get the most recent events from the log file."""
        if not self.current_log_file or not self.current_log_file.exists():
            return []
        
        events = []
        try:
            with open(self.current_log_file, 'r') as f:
                # Read lines from the end of the file
                lines = f.readlines()[-count:]
                for line in lines:
                    try:
                        event_data = json.loads(line.strip())
                        events.append(event_data)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Failed to read events: {e}")
        
        return events