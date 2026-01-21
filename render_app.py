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


# =========================
# ✅ ROOT ENDPOINT (FIX)
# =========================
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "Retail Marketing Agent API is running",
        "status": "ok",
        "available_endpoints": [
            "/api/health",
            "/api/initialize",
            "/api/generate-campaign",
            "/api/execute-campaign",
            "/api/campaign-status/<campaign_id>",
            "/api/agents",
            "/api/agents/<agent_id>"
        ]
    }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Retail Marketing Agent API"
    }), 200


@app.route('/api/initialize', methods=['POST'])
def initialize_agent():
    try:
        data = request.get_json()

        required_fields = ['client_name', 'store_type', 'location']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": f"Missing required fields: {required_fields}"
            }), 400

        agent = RetailMarketingAgent(
            client_name=data.get('client_name'),
            store_type=data.get('store_type'),
            has_online_store=data.get('has_online_store', False),
            location=data.get('location')
        )

        agent_id = f"agent_{data['client_name'].replace(' ', '_')}_{datetime.now().timestamp()}"
        agents_store[agent_id] = agent

        logger.info(f"Initialized agent: {agent_id}")

        return jsonify({
            "agent_id": agent_id,
            "status": "initialized",
            "timestamp": datetime.now().isoformat()
        }), 201

    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-campaign', methods=['POST'])
def generate_campaign():
    try:
        data = request.get_json()

        if 'agent_id' not in data:
            return jsonify({"error": "Missing agent_id"}), 400

        agent = agents_store.get(data['agent_id'])
        if not agent:
            return jsonify({"error": "Agent not found"}), 404

        campaign = agent.generate_marketing_plan(
            goal=data.get('target', 'Increase sales'),
            budget=data.get('budget', 5000),
            goal_type=data.get('goal_type', 'customer_acquisition')
        )

        return jsonify({
            "campaign_id": f"campaign_{datetime.now().timestamp()}",
            "campaign_plan": campaign
        }), 201

    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/api/execute-campaign', methods=['POST'])
def execute_campaign():
    try:
        data = request.get_json()

        if 'agent_id' not in data or 'campaign_id' not in data:
            return jsonify({"error": "Missing agent_id or campaign_id"}), 400

        agent = agents_store.get(data['agent_id'])
        if not agent:
            return jsonify({"error": "Agent not found"}), 404

        result = agent.execute_campaign(campaign_id=data['campaign_id'])

        return jsonify({
            "campaign_id": data['campaign_id'],
            "status": "executing",
            "result": result
        }), 200

    except Exception as e:
        logger.error(str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/api/campaign-status/<campaign_id>', methods=['GET'])
def get_campaign_status(campaign_id):
    return jsonify({
        "campaign_id": campaign_id,
        "status": "in_progress",
        "progress": 65,
        "updated_at": datetime.now().isoformat()
    }), 200


@app.route('/api/agents', methods=['GET'])
def list_agents():
    return jsonify({
        "total": len(agents_store),
        "agents": list(agents_store.keys())
    }), 200


@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent_info(agent_id):
    agent = agents_store.get(agent_id)
    if not agent:
        return jsonify({"error": "Agent not found"}), 404

    return jsonify({
        "agent_id": agent_id,
        "status": "active"
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "path": request.path
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
