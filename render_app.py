"""
Flask API for Retail Marketing Agent - Compatible with Render.com
Provides REST API endpoints for campaign management and AI generation
"""
import os
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import sys
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import your existing agent
from src.agents import RetailMarketingAgent, GoalType, GoalStatus

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Store agents in memory (use database in production)
agents_store = {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Retail Marketing Agent API"
    }), 200


@app.route('/api/initialize', methods=['POST'])
def initialize_agent():
    """Initialize a new marketing agent"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['client_name', 'store_type', 'location']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": f"Missing required fields: {required_fields}"
            }), 400
        
        # Extract data
        client_name = data.get('client_name')
        store_type = data.get('store_type')
        location = data.get('location')
        has_online_store = data.get('has_online_store', False)
        
        # Create agent
        agent = RetailMarketingAgent(
            client_name=client_name,
            store_type=store_type,
            has_online_store=has_online_store,
            location=location
        )
        
        # Store agent
        agent_id = f"agent_{client_name.replace(' ', '_')}_{datetime.now().timestamp()}"
        agents_store[agent_id] = agent
        
        logger.info(f"Initialized agent: {agent_id}")
        
        return jsonify({
            "agent_id": agent_id,
            "client_name": client_name,
            "store_type": store_type,
            "location": location,
            "has_online_store": has_online_store,
            "status": "initialized",
            "timestamp": datetime.now().isoformat()
        }), 201
    
    except Exception as e:
        logger.error(f"Error initializing agent: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-campaign', methods=['POST'])
def generate_campaign():
    """Generate a marketing campaign using AI"""
    try:
        data = request.get_json()
        
        # Validate
        if 'agent_id' not in data:
            return jsonify({"error": "Missing agent_id"}), 400
        
        agent_id = data.get('agent_id')
        
        # Get agent
        if agent_id not in agents_store:
            return jsonify({"error": f"Agent not found: {agent_id}"}), 404
        
        agent = agents_store[agent_id]
        
        # Extract campaign parameters
        goal_type = data.get('goal_type', 'customer_acquisition')
        target = data.get('target', 'Increase sales')
        budget = data.get('budget', 5000)
        
        # Generate campaign (using your existing method)
        campaign_result = agent.generate_marketing_plan(
            goal=target,
            budget=budget,
            goal_type=goal_type
        )
        
        campaign_id = f"campaign_{agent_id}_{datetime.now().timestamp()}"
        
        logger.info(f"Generated campaign: {campaign_id}")
        
        return jsonify({
            "campaign_id": campaign_id,
            "agent_id": agent_id,
            "goal_type": goal_type,
            "target": target,
            "budget": budget,
            "status": "draft",
            "campaign_plan": campaign_result if isinstance(campaign_result, dict) else {"plan": str(campaign_result)},
            "created_at": datetime.now().isoformat()
        }), 201
    
    except Exception as e:
        logger.error(f"Error generating campaign: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/execute-campaign', methods=['POST'])
def execute_campaign():
    """Execute a marketing campaign"""
    try:
        data = request.get_json()
        
        # Validate
        if 'campaign_id' not in data or 'agent_id' not in data:
            return jsonify({"error": "Missing campaign_id or agent_id"}), 400
        
        campaign_id = data.get('campaign_id')
        agent_id = data.get('agent_id')
        
        # Get agent
        if agent_id not in agents_store:
            return jsonify({"error": f"Agent not found: {agent_id}"}), 404
        
        agent = agents_store[agent_id]
        
        # Execute campaign (using your existing method)
        execution_result = agent.execute_campaign(campaign_id=campaign_id)
        
        logger.info(f"Executed campaign: {campaign_id}")
        
        return jsonify({
            "campaign_id": campaign_id,
            "agent_id": agent_id,
            "status": "executing",
            "execution_id": f"exec_{campaign_id}_{datetime.now().timestamp()}",
            "started_at": datetime.now().isoformat(),
            "result": execution_result if isinstance(execution_result, dict) else {"result": str(execution_result)}
        }), 200
    
    except Exception as e:
        logger.error(f"Error executing campaign: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/campaign-status/<campaign_id>', methods=['GET'])
def get_campaign_status(campaign_id):
    """Get campaign status and metrics"""
    try:
        # In production, fetch from database
        # For now, return sample status
        
        return jsonify({
            "campaign_id": campaign_id,
            "status": "in_progress",
            "metrics": {
                "impressions": 5234,
                "clicks": 342,
                "conversions": 28,
                "revenue": 4200
            },
            "progress": 65,
            "estimated_completion": "2 hours",
            "updated_at": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting campaign status: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent_info(agent_id):
    """Get agent information"""
    try:
        if agent_id not in agents_store:
            return jsonify({"error": f"Agent not found: {agent_id}"}), 404
        
        agent = agents_store[agent_id]
        
        return jsonify({
            "agent_id": agent_id,
            "client_name": getattr(agent, 'client_name', 'Unknown'),
            "store_type": getattr(agent, 'store_type', 'Unknown'),
            "location": getattr(agent, 'location', 'Unknown'),
            "status": "active"
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting agent info: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/agents', methods=['GET'])
def list_agents():
    """List all agents"""
    try:
        agents_list = []
        for agent_id in agents_store.keys():
            agents_list.append({
                "agent_id": agent_id,
                "status": "active"
            })
        
        return jsonify({
            "total": len(agents_list),
            "agents": agents_list
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


if __name__ == '__main__':
    # Get port from environment variable or default to 8000
    port = int(os.environ.get('PORT', 8000))
    
    # Create app and run
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
