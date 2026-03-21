"""Unit tests for configuration."""

import unittest
from config import Config

class TestConfig(unittest.TestCase):
    """Test configuration management."""
    
    def test_base_dir_exists(self):
        """Test that base directory exists."""
        self.assertTrue(Config.BASE_DIR.exists())
    
    def test_frontend_dir_exists(self):
        """Test that frontend directory exists."""
        self.assertTrue(Config.FRONTEND_DIR.exists())
    
    def test_database_path_exists(self):
        """Test that database path exists."""
        self.assertTrue(Config.DATABASE_PATH.exists())
    
    def test_valid_agent_states(self):
        """Test valid agent states."""
        valid_states = ['idle', 'writing', 'researching', 'executing', 'syncing', 'error']
        for state in valid_states:
            self.assertIn(state, Config.VALID_AGENT_STATES)
    
    def test_state_to_area_mapping(self):
        """Test state to area mapping."""
        self.assertIn('idle', Config.STATE_TO_AREA_MAP)
        self.assertIn('writing', Config.STATE_TO_AREA_MAP)
        self.assertIn('error', Config.STATE_TO_AREA_MAP)
    
    def test_server_config(self):
        """Test server configuration."""
        self.assertEqual(Config.HOST, "0.0.0.0")
        self.assertEqual(Config.PORT, 5000)
        self.assertTrue(Config.DEBUG)
    
    def test_sync_interval(self):
        """Test sync interval."""
        self.assertEqual(Config.SYNC_INTERVAL, 5)

if __name__ == '__main__':
    unittest.main()
