#!/usr/bin/env python3
"""Integration test for github-collab database."""
import sys
sys.path.insert(0, '.')

from services.database_service import (
    load_agents_from_db,
    load_tasks_from_db,
)

def test_agents():
    agents = load_agents_from_db()
    assert len(agents) > 0, "No agents loaded"
    
    for agent in agents:
        assert "agentId" in agent
        assert "name" in agent
        assert "state" in agent
        assert "area" in agent
        assert "type" in agent
        
    print(f"✓ Agents test passed: {len(agents)} agents")
    return True

def test_tasks():
    tasks = load_tasks_from_db()
    assert len(tasks) > 0, "No tasks loaded"
    
    for task in tasks:
        assert "id" in task
        assert "name" in task
        assert "status" in task
        
    print(f"✓ Tasks test passed: {len(tasks)} tasks")
    return True

def test_agent_detail():
    agents = load_agents_from_db()
    for agent in agents:
        if agent["state"] == "idle":
            assert "待命中" in agent["detail"] or agent["detail"] == "待命中，随时准备为你服务"
        else:
            assert agent["detail"]  # Should have some detail
            
    print("✓ Agent detail test passed")
    return True

def test_state_mapping():
    agents = load_agents_from_db()
    for agent in agents:
        state = agent["state"]
        area = agent["area"]
        
        # Verify state-to-area mapping
        if state == "idle":
            assert area == "breakroom"
        elif state in ["writing", "researching", "executing", "syncing"]:
            assert area == "writing"
        elif state == "error":
            assert area == "error"
            
    print("✓ State mapping test passed")
    return True

if __name__ == "__main__":
    print("Running integration tests...")
    print()
    
    try:
        test_agents()
        test_tasks()
        test_agent_detail()
        test_state_mapping()
        print()
        print("All tests passed! ✓")
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
