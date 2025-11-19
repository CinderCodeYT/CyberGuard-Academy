"""
Agent Coordinator Tool - Manages Agent-to-Agent (A2A) communication.

This tool handles the coordination between the Game Master and specialized agents:
1. Sends formatted A2A messages to threat actor agents
2. Manages response timeouts and retries
3. Tracks agent availability and health
4. Implements circuit breaker pattern for failing agents
5. Provides fallback mechanisms when agents are unavailable

Essential for the multi-agent architecture described in the plan.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

from cyberguard.models import AgentMessage
from cyberguard.config import settings


class AgentCoordinator:
    """
    Central coordinator for Agent-to-Agent (A2A) protocol communication.
    
    Manages reliable message passing between Game Master and specialized agents:
    - Threat Actor agents (Phishing, Vishing, BEC, etc.)
    - Evaluation agent for assessment tracking  
    - Memory agent for session storage
    
    Implements resilience patterns like retries, timeouts, and circuit breakers.
    """
    
    def __init__(self):
        self.agent_endpoints = {}
        self.agent_health = {}
        self.circuit_breakers = {}
        self.message_history = {}
        self.is_initialized = False

    async def initialize(self) -> None:
        """Initialize agent registry and communication channels."""
        print("[AgentCoordinator] Initializing A2A communication...")
        
        # In production, this would discover agent endpoints
        self.agent_endpoints = await self._discover_agent_endpoints()
        
        # Initialize health tracking
        self.agent_health = {
            agent: {"status": "unknown", "last_check": None, "failure_count": 0}
            for agent in self.agent_endpoints.keys()
        }
        
        # Initialize circuit breakers
        self.circuit_breakers = {
            agent: {"state": "closed", "failure_count": 0, "last_failure": None}
            for agent in self.agent_endpoints.keys()
        }
        
        # Initialize message tracking
        self.message_history = {}
        
        self.is_initialized = True
        print(f"[AgentCoordinator] Registered {len(self.agent_endpoints)} agents")

    async def shutdown(self) -> None:
        """Clean up communication resources."""
        print("[AgentCoordinator] Shutting down agent coordinator")
        
        # Notify all agents of shutdown if needed
        for agent_name in self.agent_endpoints.keys():
            try:
                await self._send_shutdown_notification(agent_name)
            except Exception as e:
                print(f"[AgentCoordinator] Warning: Could not notify {agent_name} of shutdown: {e}")
        
        self.agent_endpoints.clear()
        self.agent_health.clear()
        self.circuit_breakers.clear()

    async def send_message(
        self,
        target_agent: str,
        message: AgentMessage,
        timeout_seconds: float = 30.0,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Send A2A message to target agent with retry logic.
        
        Args:
            target_agent: Name of recipient agent
            message: Formatted A2A message
            timeout_seconds: Maximum wait time for response
            max_retries: Number of retry attempts on failure
            
        Returns:
            Response from target agent or error information
        """
        if not self.is_initialized:
            await self.initialize()
        
        print(f"[AgentCoordinator] Sending {message.message_type} to {target_agent}")
        
        # Check circuit breaker
        if not self._check_circuit_breaker(target_agent):
            return {
                "error": "circuit_breaker_open",
                "message": f"Agent {target_agent} is currently unavailable due to repeated failures"
            }
        
        # Track message
        self._track_outbound_message(message)
        
        # Attempt delivery with retries
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    await asyncio.sleep(min(2 ** attempt, 10))  # Exponential backoff
                
                response = await self._deliver_message(target_agent, message, timeout_seconds)
                
                # Success - reset circuit breaker
                self._record_success(target_agent)
                self._track_response(message.correlation_id, response)
                
                return response
                
            except Exception as e:
                last_error = e
                print(f"[AgentCoordinator] Attempt {attempt + 1} failed for {target_agent}: {str(e)}")
                
                # Record failure
                self._record_failure(target_agent, str(e))
        
        # All attempts failed
        error_response = {
            "error": "delivery_failed",
            "target_agent": target_agent,
            "attempts": max_retries + 1,
            "last_error": str(last_error),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self._track_response(message.correlation_id, error_response)
        return error_response

    async def check_agent_availability(self, agent_names: List[str]) -> List[str]:
        """
        Check which agents are currently available.
        
        Args:
            agent_names: List of agent names to check
            
        Returns:
            List of available agent names
        """
        available_agents = []
        
        for agent_name in agent_names:
            try:
                # Send ping message
                ping_message = AgentMessage(
                    sender_agent="game_master",
                    recipient_agent=agent_name,
                    message_type="ping",
                    payload={"timestamp": time.time()},
                    session_id="health_check"
                )
                
                response = await self.send_message(
                    target_agent=agent_name,
                    message=ping_message,
                    timeout_seconds=5.0,
                    max_retries=1
                )
                
                if "error" not in response:
                    available_agents.append(agent_name)
                    self._update_agent_health(agent_name, "available")
                else:
                    self._update_agent_health(agent_name, "unavailable")
                    
            except Exception as e:
                print(f"[AgentCoordinator] Health check failed for {agent_name}: {str(e)}")
                self._update_agent_health(agent_name, "error")
        
        return available_agents

    async def broadcast_message(
        self,
        message: AgentMessage,
        target_agents: List[str],
        wait_for_all: bool = False
    ) -> Dict[str, Any]:
        """
        Broadcast message to multiple agents.
        
        Args:
            message: Message to broadcast
            target_agents: List of recipient agents
            wait_for_all: Whether to wait for all responses
            
        Returns:
            Dictionary mapping agent names to their responses
        """
        print(f"[AgentCoordinator] Broadcasting {message.message_type} to {len(target_agents)} agents")
        
        # Create individual messages for each agent
        tasks = []
        for agent_name in target_agents:
            agent_message = AgentMessage(
                sender_agent=message.sender_agent,
                recipient_agent=agent_name,
                message_type=message.message_type,
                payload=message.payload.copy(),
                session_id=message.session_id
            )
            
            task = asyncio.create_task(
                self.send_message(agent_name, agent_message),
                name=f"broadcast_to_{agent_name}"
            )
            tasks.append((agent_name, task))
        
        responses = {}
        
        if wait_for_all:
            # Wait for all responses
            for agent_name, task in tasks:
                try:
                    responses[agent_name] = await task
                except Exception as e:
                    responses[agent_name] = {"error": f"broadcast_failed: {str(e)}"}
        else:
            # Collect responses as they come in
            done_tasks = []
            pending_tasks = [task for _, task in tasks]
            
            while pending_tasks:
                done, pending = await asyncio.wait(
                    pending_tasks, 
                    timeout=10.0, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    # Find corresponding agent name
                    agent_name = next(name for name, t in tasks if t == task)
                    try:
                        responses[agent_name] = await task
                    except Exception as e:
                        responses[agent_name] = {"error": f"broadcast_failed: {str(e)}"}
                
                pending_tasks = list(pending)
            
            # Cancel any remaining tasks
            for task in pending_tasks:
                task.cancel()
        
        print(f"[AgentCoordinator] Broadcast complete: {len(responses)} responses received")
        return responses

    async def _discover_agent_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Discover available agent endpoints."""
        
        # In production, this would query a service registry or configuration
        # For development, we'll use mock endpoints
        
        if settings.is_development and settings.mock_agents_in_tests:
            return {
                "phishing_agent": {
                    "endpoint": "mock://phishing_agent",
                    "type": "threat_actor",
                    "capabilities": ["generate_scenario", "adapt_scenario"]
                },
                "vishing_agent": {
                    "endpoint": "mock://vishing_agent", 
                    "type": "threat_actor",
                    "capabilities": ["generate_scenario", "simulate_call"]
                },
                "bec_agent": {
                    "endpoint": "mock://bec_agent",
                    "type": "threat_actor", 
                    "capabilities": ["generate_scenario", "executive_impersonation"]
                },
                "evaluation_agent": {
                    "endpoint": "mock://evaluation_agent",
                    "type": "evaluator",
                    "capabilities": ["track_decision", "evaluate_session", "calculate_risk"]
                },
                "memory_agent": {
                    "endpoint": "mock://memory_agent",
                    "type": "memory",
                    "capabilities": ["store_session", "get_user_profile", "update_patterns"]
                }
            }
        else:
            # Production endpoint discovery would go here
            return {
                "phishing_agent": {
                    "endpoint": f"https://{settings.google_cloud_region}-{settings.google_cloud_project}.cloudfunctions.net/phishing-agent",
                    "type": "threat_actor",
                    "capabilities": ["generate_scenario", "adapt_scenario"]
                }
                # ... other production endpoints
            }

    async def _deliver_message(
        self,
        target_agent: str,
        message: AgentMessage,
        timeout_seconds: float
    ) -> Dict[str, Any]:
        """Deliver message to specific agent."""
        
        if target_agent not in self.agent_endpoints:
            raise ValueError(f"Unknown agent: {target_agent}")
        
        endpoint_info = self.agent_endpoints[target_agent]
        endpoint_url = endpoint_info["endpoint"]
        
        # Handle different endpoint types
        if endpoint_url.startswith("mock://"):
            return await self._handle_mock_delivery(target_agent, message)
        elif endpoint_url.startswith("https://"):
            return await self._handle_http_delivery(endpoint_url, message, timeout_seconds)
        else:
            raise ValueError(f"Unsupported endpoint type: {endpoint_url}")

    async def _handle_mock_delivery(self, target_agent: str, message: AgentMessage) -> Dict[str, Any]:
        """Handle delivery to mock agents for testing."""
        
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Generate mock responses based on message type
        if message.message_type == "ping":
            return {
                "message_type": "pong",
                "agent": target_agent,
                "status": "healthy",
                "timestamp": time.time()
            }
        elif message.message_type == "generate_scenario":
            return {
                "message_type": "scenario_ready",
                "scenario_content": {
                    "threat_type": "phishing",
                    "subject": "URGENT: Account Verification Required",
                    "body": "Your account will be suspended unless you verify...",
                    "red_flags": ["urgency", "external_domain", "credential_request"],
                    "difficulty": message.payload.get("difficulty", 3)
                },
                "agent": target_agent
            }
        elif message.message_type == "track_decision":
            return {
                "message_type": "decision_tracked",
                "status": "recorded",
                "agent": target_agent
            }
        elif message.message_type == "evaluate_session":
            return {
                "message_type": "evaluation_complete",
                "evaluation_results": {
                    "overall_score": 0.75,
                    "risk_score": 0.35,
                    "decisions_analyzed": 3,
                    "recommendations": ["focus_on_email_headers", "practice_urgency_recognition"]
                },
                "agent": target_agent
            }
        else:
            return {
                "message_type": "acknowledged",
                "original_type": message.message_type,
                "status": "processed",
                "agent": target_agent
            }

    async def _handle_http_delivery(
        self,
        endpoint_url: str,
        message: AgentMessage,
        timeout_seconds: float
    ) -> Dict[str, Any]:
        """Handle delivery to HTTP endpoints."""
        
        # This would use httpx or similar for actual HTTP delivery
        # For now, just a placeholder
        
        import httpx
        
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(
                endpoint_url,
                json=message.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()

    def _check_circuit_breaker(self, agent_name: str) -> bool:
        """Check if circuit breaker allows communication with agent."""
        
        if agent_name not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[agent_name]
        
        # If circuit is closed (normal operation), allow
        if breaker["state"] == "closed":
            return True
        
        # If circuit is open, check if enough time has passed to try again
        if breaker["state"] == "open":
            if breaker["last_failure"]:
                time_since_failure = datetime.utcnow() - breaker["last_failure"]
                if time_since_failure > timedelta(minutes=5):  # Try again after 5 minutes
                    breaker["state"] = "half_open"
                    return True
            return False
        
        # If half-open, allow one attempt
        if breaker["state"] == "half_open":
            return True
        
        return False

    def _record_success(self, agent_name: str) -> None:
        """Record successful communication with agent."""
        
        if agent_name in self.circuit_breakers:
            self.circuit_breakers[agent_name].update({
                "state": "closed",
                "failure_count": 0,
                "last_failure": None
            })
        
        if agent_name in self.agent_health:
            self.agent_health[agent_name].update({
                "status": "healthy",
                "last_check": datetime.utcnow(),
                "failure_count": 0
            })

    def _record_failure(self, agent_name: str, error_message: str) -> None:
        """Record failed communication with agent."""
        
        if agent_name in self.circuit_breakers:
            breaker = self.circuit_breakers[agent_name]
            breaker["failure_count"] += 1
            breaker["last_failure"] = datetime.utcnow()
            
            # Open circuit breaker after 3 failures
            if breaker["failure_count"] >= 3:
                breaker["state"] = "open"
                print(f"[AgentCoordinator] Circuit breaker opened for {agent_name} after {breaker['failure_count']} failures")
        
        if agent_name in self.agent_health:
            health = self.agent_health[agent_name]
            health["failure_count"] += 1
            health["status"] = "error"
            health["last_check"] = datetime.utcnow()
            health["last_error"] = error_message

    def _update_agent_health(self, agent_name: str, status: str) -> None:
        """Update agent health status."""
        
        if agent_name in self.agent_health:
            self.agent_health[agent_name].update({
                "status": status,
                "last_check": datetime.utcnow()
            })

    def _track_outbound_message(self, message: AgentMessage) -> None:
        """Track outbound message for monitoring."""
        
        self.message_history[message.correlation_id] = {
            "message": message.model_dump(),
            "sent_at": datetime.utcnow(),
            "status": "sent"
        }

    def _track_response(self, correlation_id: str, response: Dict[str, Any]) -> None:
        """Track response for monitoring."""
        
        if correlation_id in self.message_history:
            self.message_history[correlation_id].update({
                "response": response,
                "completed_at": datetime.utcnow(),
                "status": "completed"
            })

    async def _send_shutdown_notification(self, agent_name: str) -> None:
        """Send shutdown notification to agent."""
        
        try:
            shutdown_message = AgentMessage(
                sender_agent="game_master",
                recipient_agent=agent_name,
                message_type="shutdown_notification",
                payload={"reason": "system_shutdown"},
                session_id="system"
            )
            
            await self._deliver_message(agent_name, shutdown_message, 5.0)
        except Exception:
            # Ignore errors during shutdown
            pass

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all registered agents."""
        
        return {
            "registered_agents": len(self.agent_endpoints),
            "agent_health": self.agent_health.copy(),
            "circuit_breakers": self.circuit_breakers.copy(),
            "total_messages": len(self.message_history),
            "last_updated": datetime.utcnow().isoformat()
        }