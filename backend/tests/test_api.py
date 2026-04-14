"""Unit tests for API endpoints."""

import unittest
import json
from pathlib import Path
from flask import Flask
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAgentsAPI(unittest.TestCase):
    """Tests for agents API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        from main import create_app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_get_all_agents(self):
        """Test GET /api/v1/agents endpoint."""
        response = self.client.get('/api/v1/agents')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ok', data)
        self.assertIn('agents', data)
    
    def test_get_agent_by_id(self):
        """Test GET /api/v1/agents/<id> endpoint."""
        response = self.client.get('/api/v1/agents/test-agent')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ok', data)
    
    def test_update_agent_status_valid(self):
        """Test POST /api/v1/agents/<id>/status with valid input."""
        response = self.client.post(
            '/api/v1/agents/test-agent/status',
            data=json.dumps({'state': 'writing'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ok', data)
    
    def test_update_agent_status_invalid_state(self):
        """Test POST with invalid state (should normalize)."""
        response = self.client.post(
            '/api/v1/agents/test-agent/status',
            data=json.dumps({'state': 'waiting'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # 'waiting' should be normalized to 'idle'
        self.assertEqual(data.get('state'), 'idle')
    
    def test_update_agent_status_missing_state(self):
        """Test POST with missing state parameter."""
        response = self.client.post(
            '/api/v1/agents/test-agent/status',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])


class TestTasksAPI(unittest.TestCase):
    """Tests for tasks API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        from main import create_app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_get_all_tasks(self):
        """Test GET /api/v1/tasks endpoint."""
        response = self.client.get('/api/v1/tasks')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ok', data)
        self.assertIn('tasks', data)


class TestStateAPI(unittest.TestCase):
    """Tests for state API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        from main import create_app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_get_current_state(self):
        """Test GET /api/v1/state endpoint."""
        response = self.client.get('/api/v1/state')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ok', data)
        self.assertIn('state', data)


class TestAssetsAPI(unittest.TestCase):
    """Tests for assets API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        from main import create_app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_get_asset_positions(self):
        """Test GET /api/v1/assets/positions endpoint."""
        response = self.client.get('/api/v1/assets/positions')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ok', data)
        self.assertIn('positions', data)
    
    def test_update_asset_positions_valid(self):
        """Test POST /api/v1/assets/positions with valid input."""
        positions = {'agent1': {'x': 100, 'y': 200}}
        response = self.client.post(
            '/api/v1/assets/positions',
            data=json.dumps(positions),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])
    
    def test_update_asset_positions_invalid(self):
        """Test POST with invalid positions (not a dict)."""
        response = self.client.post(
            '/api/v1/assets/positions',
            data=json.dumps('invalid'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])


class TestConfigAPI(unittest.TestCase):
    """Tests for config API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        from main import create_app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_get_config(self):
        """Test GET /api/v1/config endpoint."""
        response = self.client.get('/api/v1/config')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ok', data)
        self.assertIn('config', data)
    
    def test_update_config_valid(self):
        """Test POST /api/v1/config with valid input."""
        config = {'custom_config': {'theme': 'dark'}}
        response = self.client.post(
            '/api/v1/config',
            data=json.dumps(config),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['ok'])


class TestJoinKeysAPI(unittest.TestCase):
    """Tests for join keys API endpoints."""
    
    def setUp(self):
        """Set up test client."""
        from main import create_app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_get_join_keys(self):
        """Test GET /api/v1/join-keys endpoint."""
        response = self.client.get('/api/v1/join-keys')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ok', data)
        self.assertIn('keys', data)


class TestAPIVersioning(unittest.TestCase):
    """Tests for API versioning."""
    
    def setUp(self):
        """Set up test client."""
        from main import create_app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_api_version_endpoint(self):
        """Test GET /api/version endpoint."""
        response = self.client.get('/api/version')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['version'], 'v1')
        self.assertIn('endpoints', data)
    
    def test_health_endpoint(self):
        """Test GET /health endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], 'v1')
    
    def test_versioned_endpoints(self):
        """Test that all endpoints use /api/v1/ prefix."""
        endpoints = [
            '/api/v1/agents',
            '/api/v1/tasks',
            '/api/v1/state',
            '/api/v1/assets/positions',
            '/api/v1/config',
            '/api/v1/join-keys',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Should not return 404
            self.assertNotEqual(response.status_code, 404, 
                              msg=f"Endpoint {endpoint} returned 404")


class TestInputValidation(unittest.TestCase):
    """Tests for input validation."""
    
    def setUp(self):
        """Set up test client."""
        from main import create_app
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
    
    def test_agent_status_validation(self):
        """Test that invalid agent status is normalized."""
        # Test various invalid states
        invalid_states = ['INVALID_STATE', 'xyz', '']
        
        for state in invalid_states:
            response = self.client.post(
                '/api/v1/agents/test/status',
                data=json.dumps({'state': state}),
                content_type='application/json'
            )
            # Should return 400 for empty or 200 with normalized state
            data = json.loads(response.data)
            if state == '':
                self.assertEqual(response.status_code, 400)
            else:
                # Invalid states should be normalized to 'idle'
                self.assertIn('state', data)
    
    def test_asset_positions_validation(self):
        """Test that invalid asset positions are rejected."""
        # Test with non-dict value
        response = self.client.post(
            '/api/v1/assets/positions',
            data=json.dumps(['not', 'a', 'dict']),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['ok'])


if __name__ == '__main__':
    unittest.main()
