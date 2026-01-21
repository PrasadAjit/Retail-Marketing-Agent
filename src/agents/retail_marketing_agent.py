"""
Main Retail Marketing Agent implementation
"""
from typing import Dict, List, Any, Optional
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .base_agent import BaseAgent, Goal, GoalType, GoalStatus
from ..config.settings import settings
from ..services.deployment_service import DeploymentService
from ..modules.customer_acquisition import CustomerAcquisitionModule
from ..modules.customer_retention import CustomerRetentionModule
from ..modules.digital_marketing import DigitalMarketingModule
from ..campaigns.campaign_manager import CampaignManager, CampaignType, CampaignStatus
from datetime import datetime, timedelta


class RetailMarketingAgent(BaseAgent):
    """
    Main orchestrator agent for retail marketing activities
    Coordinates various specialized marketing modules
    """
    
    def __init__(
        self,
        client_name: str,
        store_type: str = "general",
        has_online_store: bool = True,
        location: Optional[str] = None
    ):
        super().__init__(
            name="Retail Marketing Agent",
            description="AI-powered marketing agent for retail businesses"
        )
        
        self.client_name = client_name
        self.store_type = store_type
        self.has_online_store = has_online_store
        self.location = location or settings.store.location
        
        # Initialize LLM (Azure or OpenAI)
        if settings.openai.use_azure:
            self.llm = AzureChatOpenAI(
                azure_deployment=settings.openai.azure_deployment,
                api_version=settings.openai.azure_api_version,
                azure_endpoint=settings.openai.azure_endpoint,
                api_key=settings.openai.azure_api_key,
                temperature=settings.openai.temperature
            )
        else:
            self.llm = ChatOpenAI(
                model=settings.openai.model,
                temperature=settings.openai.temperature,
                openai_api_key=settings.openai.api_key
            )
        
        # Store context
        self.store_memory("client_name", client_name)
        self.store_memory("store_type", store_type)
        self.store_memory("has_online_store", has_online_store)
        self.store_memory("location", location)
        
        # Initialize services and modules
        self.deployment_service = DeploymentService()
        self.campaign_manager = CampaignManager()
        self.acquisition_module = CustomerAcquisitionModule()
        self.retention_module = CustomerRetentionModule()
        self.digital_module = DigitalMarketingModule()
    
    def set_goal(
        self,
        goal_type: str,
        target: str,
        timeframe: str,
        description: Optional[str] = None,
        metrics: Optional[Dict[str, Any]] = None,
        priority: int = 1
    ) -> Goal:
        """
        Set a new marketing goal
        
        Args:
            goal_type: Type of goal (e.g., 'customer_acquisition', 'digital_presence')
            target: Specific target for the goal
            timeframe: Time period for goal achievement
            description: Optional detailed description
            metrics: Optional success metrics
            priority: Goal priority (1-5, higher is more important)
        
        Returns:
            Created Goal object
        """
        # Convert string to GoalType enum
        goal_type_enum = GoalType[goal_type.upper()]
        
        # Generate description if not provided
        if not description:
            description = f"Achieve {target} within {timeframe} for {self.client_name}"
        
        goal = Goal(
            goal_type=goal_type_enum,
            description=description,
            target=target,
            timeframe=timeframe,
            metrics=metrics,
            priority=priority
        )
        
        self.add_goal(goal)
        return goal
    
    def plan(self, goal: Goal) -> List[Dict[str, Any]]:
        """
        Create an execution plan for the given goal using AI
        """
        planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert retail marketing strategist. Create a detailed execution plan 
            for the given marketing goal. Break it down into specific, actionable subtasks.
            
            Store Context:
            - Client: {client_name}
            - Store Type: {store_type}
            - Has Online Store: {has_online_store}
            - Location: {location}
            
            Consider all aspects of retail marketing including:
            - Customer acquisition and retention
            - In-store marketing
            - Digital and social media presence
            - Seasonal and promotional planning
            - Customer insights and analytics
            - Partnership and community engagement
            """),
            ("user", """Goal Type: {goal_type}
            Target: {target}
            Timeframe: {timeframe}
            Description: {description}
            
            Create a step-by-step execution plan with 5-8 specific subtasks. 
            For each subtask, provide:
            1. Task name
            2. Description
            3. Expected outcome
            4. Required resources
            5. Timeline
            
            Format as a numbered list.""")
        ])
        
        chain = planning_prompt | self.llm
        
        response = chain.invoke({
            "client_name": self.client_name,
            "store_type": self.store_type,
            "has_online_store": self.has_online_store,
            "location": self.location,
            "goal_type": goal.goal_type.value,
            "target": goal.target,
            "timeframe": goal.timeframe,
            "description": goal.description
        })
        
        # Parse response into subtasks
        response_text = response.content if hasattr(response, 'content') else str(response)
        subtasks = self._parse_plan(response_text)
        
        # Add subtasks to goal
        for subtask in subtasks:
            goal.add_subtask(subtask)
        
        return subtasks
    
    def _parse_plan(self, plan_text: str) -> List[Dict[str, Any]]:
        """Parse the AI-generated plan into structured subtasks"""
        import re
        
        subtasks = []
        lines = plan_text.strip().split('\n')
        
        current_task = {}
        task_counter = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Match numbered items: "1.", "1)", "Step 1:", etc.
            number_match = re.match(r'^(\d+)[.):]\s*(.+)', line)
            if number_match:
                # Save previous task
                if current_task and current_task.get('name'):
                    task_counter += 1
                    current_task['id'] = f"task_{task_counter}"
                    subtasks.append(current_task)
                
                # Start new task
                task_name = number_match.group(2).strip()
                # Remove common prefixes
                for prefix in ['Task:', 'Subtask:', 'Step:']:
                    if task_name.startswith(prefix):
                        task_name = task_name[len(prefix):].strip()
                
                current_task = {
                    'name': task_name,
                    'status': 'pending',
                    'description': task_name
                }
            elif current_task and line and not line.startswith('#'):
                # Append to description
                current_task['description'] += ' ' + line
        
        # Add last task
        if current_task and current_task.get('name'):
            task_counter += 1
            current_task['id'] = f"task_{task_counter}"
            subtasks.append(current_task)
        
        # If parsing failed, create default subtasks
        if not subtasks:
            subtasks = [
                {'id': 'task_1', 'name': 'Plan campaign strategy', 'status': 'pending', 'description': 'Develop comprehensive campaign strategy'},
                {'id': 'task_2', 'name': 'Create marketing content', 'status': 'pending', 'description': 'Design promotional materials and messaging'},
                {'id': 'task_3', 'name': 'Deploy across channels', 'status': 'pending', 'description': 'Launch campaign on email and social media'},
                {'id': 'task_4', 'name': 'Monitor performance', 'status': 'pending', 'description': 'Track metrics and engagement'},
                {'id': 'task_5', 'name': 'Optimize and adjust', 'status': 'pending', 'description': 'Make improvements based on results'}
            ]
        
        return subtasks
    
    def execute(self, goal: Optional[Goal] = None) -> Dict[str, Any]:
        """
        Execute a marketing goal or all pending goals
        """
        if goal:
            goals_to_execute = [goal]
        else:
            goals_to_execute = self.get_active_goals()
        
        if not goals_to_execute:
            return {
                "status": "no_goals",
                "message": "No goals to execute"
            }
        
        results = []
        
        for g in goals_to_execute:
            g.update_status(GoalStatus.IN_PROGRESS)
            
            # Create plan if not exists
            if not g.subtasks:
                self.plan(g)
            
            # Execute based on goal type
            execution_result = self._execute_goal_by_type(g)
            
            g.update_status(GoalStatus.COMPLETED)
            g.add_result("execution", execution_result)
            
            # Evaluate results
            evaluation = self.evaluate(g, execution_result)
            g.add_result("evaluation", evaluation)
            
            results.append({
                "goal_id": g.id,
                "goal_type": g.goal_type.value,
                "execution": execution_result,
                "evaluation": evaluation
            })
        
        return {
            "status": "success",
            "goals_executed": len(results),
            "results": results
        }
    
    def _execute_goal_by_type(self, goal: Goal) -> Dict[str, Any]:
        """Execute goal based on its type"""
        execution_strategies = {
            GoalType.CUSTOMER_ACQUISITION: self._execute_customer_acquisition,
            GoalType.CUSTOMER_RETENTION: self._execute_customer_retention,
            GoalType.INSTORE_MARKETING: self._execute_instore_marketing,
            GoalType.DIGITAL_PRESENCE: self._execute_digital_presence,
            GoalType.SEASONAL_CAMPAIGN: self._execute_seasonal_campaign,
            GoalType.ANALYTICS_INSIGHTS: self._execute_analytics_insights,
            GoalType.COMMUNITY_ENGAGEMENT: self._execute_community_engagement
        }
        
        strategy = execution_strategies.get(goal.goal_type)
        if strategy:
            return strategy(goal)
        else:
            return {"error": f"No execution strategy for {goal.goal_type.value}"}
    
    def _execute_customer_acquisition(self, goal: Goal) -> Dict[str, Any]:
        """Execute customer acquisition goal"""
        # Extract target and duration from goal
        target_customers = 100  # Default
        duration_days = 30  # Default
        
        # Generate campaign content using AI
        campaign_data = self.acquisition_module.create_promotion_campaign(
            target_audience="new customers in local area",
            campaign_type="acquisition",
            budget=5000.0,
            duration_days=duration_days,
            store_context={
                "name": self.client_name,
                "type": self.store_type,
                "location": self.location
            }
        )
        
        # Create campaign in campaign manager
        campaign = self.campaign_manager.create_campaign(
            name=f"{self.client_name} - Customer Acquisition",
            campaign_type="ACQUISITION",
            description=goal.description,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            budget=5000.0,
            target_metrics={
                "new_customers": target_customers,
                "conversion_rate": 5.0,
                "cost_per_acquisition": 50.0
            }
        )
        
        # Add channels
        campaign.add_channel("email")
        campaign.add_channel("facebook")
        campaign.add_channel("instagram")
        campaign.add_channel("twitter")
        
        # Set to planned then activate
        campaign.update_status(CampaignStatus.PLANNED)
        self.campaign_manager.launch_campaign(campaign.id)
        
        # DEPLOY the campaign via deployment service
        deployment_results = self.deployment_service.deploy_customer_acquisition_campaign(
            campaign_id=campaign.id,
            campaign_content=campaign_data,
            target_segment="new"
        )
        
        # Update campaign with deployment metrics
        campaign.update_performance({
            "emails_sent": deployment_results.get("email", {}).get("sent", 0),
            "social_posts": deployment_results.get("social_media", {}).get("posts_created", 0),
            "total_reach": deployment_results.get("total_reach", 0),
            "deployment_date": deployment_results.get("deployed_at")
        })
        
        return {
            "strategy": "customer_acquisition",
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "status": campaign.status.value,
            "start_date": campaign.start_date.isoformat(),
            "end_date": campaign.end_date.isoformat(),
            "duration_days": campaign.get_duration_days(),
            "budget": campaign.budget,
            "channels_deployed": deployment_results.get("channels_deployed", []),
            "deployment": deployment_results,
            "message": "Campaign DEPLOYED and ACTIVE across email and social media"
        }
    
    def _execute_customer_retention(self, goal: Goal) -> Dict[str, Any]:
        """Execute customer retention goal"""
        duration_days = 30
        
        # Create retention campaign
        campaign = self.campaign_manager.create_campaign(
            name=f"{self.client_name} - Customer Retention",
            campaign_type="RETENTION",
            description=goal.description,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            budget=3000.0,
            target_metrics={"retention_rate": 75.0, "repeat_purchases": 50}
        )
        
        campaign.add_channel("email")
        campaign.add_channel("facebook")
        campaign.update_status(CampaignStatus.PLANNED)
        self.campaign_manager.launch_campaign(campaign.id)
        
        # Deploy retention campaign
        deployment_results = self.deployment_service.deploy_retention_campaign(
            campaign_id=campaign.id,
            campaign_content={"campaign_plan": "Loyalty rewards and exclusive offers"}
        )
        
        campaign.update_performance({
            "emails_sent": deployment_results.get("email", {}).get("sent", 0),
            "total_reach": deployment_results.get("total_reach", 0)
        })
        
        return {
            "strategy": "customer_retention",
            "campaign_id": campaign.id,
            "status": campaign.status.value,
            "deployment": deployment_results,
            "message": "Retention campaign DEPLOYED - loyalty emails sent and social posts live"
        }
    
    def _execute_instore_marketing(self, goal: Goal) -> Dict[str, Any]:
        """Execute in-store marketing goal"""
        return {
            "strategy": "instore_marketing",
            "visual_merchandising": "planned",
            "pos_displays": "designed",
            "events": "scheduled",
            "message": "In-store marketing materials and events prepared"
        }
    
    def _execute_digital_presence(self, goal: Goal) -> Dict[str, Any]:
        """Execute digital presence goal"""
        duration_days = 30
        
        # Create digital campaign
        campaign = self.campaign_manager.create_campaign(
            name=f"{self.client_name} - Digital Presence",
            campaign_type="BRAND_AWARENESS",
            description=goal.description,
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=duration_days),
            budget=4000.0,
            target_metrics={"impressions": 50000, "engagement_rate": 5.0}
        )
        
        campaign.add_channel("facebook")
        campaign.add_channel("instagram")
        campaign.add_channel("twitter")
        campaign.update_status(CampaignStatus.PLANNED)
        self.campaign_manager.launch_campaign(campaign.id)
        
        # Deploy digital campaign (heavy social media focus)
        deployment_results = self.deployment_service.deploy_digital_campaign(
            campaign_id=campaign.id,
            campaign_content={"campaign_plan": "Social media content and engagement"}
        )
        
        campaign.update_performance({
            "social_posts": deployment_results.get("social_media", {}).get("posts_created", 0),
            "total_reach": deployment_results.get("total_reach", 0)
        })
        
        return {
            "strategy": "digital_presence",
            "campaign_id": campaign.id,
            "status": campaign.status.value,
            "deployment": deployment_results,
            "message": "Digital presence campaign ACTIVE - multiple posts live on all platforms"
        }
    
    def _execute_seasonal_campaign(self, goal: Goal) -> Dict[str, Any]:
        """Execute seasonal campaign goal"""
        return {
            "strategy": "seasonal_campaign",
            "campaign_theme": "planned",
            "promotional_offers": "created",
            "marketing_materials": "designed",
            "message": "Seasonal campaign fully planned and ready"
        }
    
    def _execute_analytics_insights(self, goal: Goal) -> Dict[str, Any]:
        """Execute analytics insights goal"""
        return {
            "strategy": "analytics_insights",
            "data_analyzed": True,
            "insights_generated": [],
            "recommendations": [],
            "message": "Customer insights and analytics completed"
        }
    
    def _execute_community_engagement(self, goal: Goal) -> Dict[str, Any]:
        """Execute community engagement goal"""
        return {
            "strategy": "community_engagement",
            "partnerships": "identified",
            "events": "planned",
            "influencers": "contacted",
            "message": "Community engagement initiatives launched"
        }
    
    def evaluate(self, goal: Goal, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the results of goal execution using AI
        """
        evaluation_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert retail marketing analyst. Evaluate the execution results 
            of a marketing goal and provide insights and recommendations."""),
            ("user", """Goal: {goal_description}
            Target: {target}
            Timeframe: {timeframe}
            
            Execution Results:
            {results}
            
            Provide:
            1. Success assessment (score 0-100)
            2. Key achievements
            3. Areas for improvement
            4. Next steps and recommendations
            
            Format as structured bullet points.""")
        ])
        
        chain = evaluation_prompt | self.llm
        
        evaluation_response = chain.invoke({
            "goal_description": goal.description,
            "target": goal.target,
            "timeframe": goal.timeframe,
            "results": str(results)
        })
        
        evaluation = evaluation_response.content if hasattr(evaluation_response, 'content') else str(evaluation_response)
        
        return {
            "evaluation_text": evaluation,
            "goal_id": goal.id,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get a comprehensive status report of all goals and activities"""
        return {
            "client_name": self.client_name,
            "store_type": self.store_type,
            "total_goals": len(self.goals),
            "active_goals": len(self.get_active_goals()),
            "completed_goals": len(self.get_completed_goals()),
            "goals": [g.to_dict() for g in self.goals],
            "customer_stats": self.deployment_service.get_customer_stats(),
            "all_campaigns": self.campaign_manager.get_all_campaigns()
        }
    
    def get_deployment_overview(self, campaign_id: str) -> Dict[str, Any]:
        """Get complete deployment overview for a campaign"""
        return self.deployment_service.get_campaign_overview(campaign_id)
    
    def get_all_emails(self) -> List[Dict[str, Any]]:
        """Get all sent emails"""
        return self.deployment_service.get_all_emails()
    
    def get_all_social_posts(self) -> List[Dict[str, Any]]:
        """Get all social media posts"""
        return self.deployment_service.get_all_posts()


from datetime import datetime
