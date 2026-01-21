"""
Gradio Web Interface for Retail Marketing Agent
Provides interactive UI for goal setting, execution monitoring, and metrics tracking
"""
import gradio as gr
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import RetailMarketingAgent, GoalType, GoalStatus
from src.config.settings import settings


class MarketingAgentUI:
    """Gradio UI wrapper for Retail Marketing Agent"""
    
    def __init__(self):
        self.agent: Optional[RetailMarketingAgent] = None
        self.execution_logs: List[str] = []
        self.current_goal = None
        self.pending_campaign = None  # Store campaign content for approval
        self.campaign_content_draft = ""
        
    def initialize_agent(
        self,
        client_name: str,
        store_type: str,
        has_online_store: bool,
        location: str
    ) -> str:
        """Initialize the marketing agent"""
        try:
            self.agent = RetailMarketingAgent(
                client_name=client_name,
                store_type=store_type,
                has_online_store=has_online_store,
                location=location
            )
            self.execution_logs.append(f"✓ Agent initialized for {client_name}")
            return f"✅ Agent initialized successfully for **{client_name}**\n\nStore Type: {store_type}\nLocation: {location}\nOnline Store: {'Yes' if has_online_store else 'No'}"
        except Exception as e:
            error_msg = f"❌ Error initializing agent: {str(e)}"
            self.execution_logs.append(error_msg)
            return error_msg
    
    def set_goal(
        self,
        goal_type: str,
        target: str,
        timeframe: str,
        description: str,
        priority: int
    ) -> tuple[str, str]:
        """Set a new marketing goal"""
        if not self.agent:
            return "❌ Please initialize the agent first", ""
        
        try:
            self.execution_logs.append(f"\n📋 Setting new goal: {goal_type}")
            
            goal = self.agent.set_goal(
                goal_type=goal_type.lower().replace(" ", "_"),
                target=target,
                timeframe=timeframe,
                description=description,
                priority=priority
            )
            
            self.current_goal = goal
            
            log_msg = f"✓ Goal created: {goal.id}"
            self.execution_logs.append(log_msg)
            
            result = f"""✅ **Goal Created Successfully**

**Goal ID:** {goal.id}
**Type:** {goal.goal_type.value}
**Target:** {target}
**Timeframe:** {timeframe}
**Priority:** {priority}/5
**Status:** {goal.status.value}

**Description:** {description}
"""
            
            return result, "\n".join(self.execution_logs[-10:])
            
        except Exception as e:
            error_msg = f"❌ Error setting goal: {str(e)}"
            self.execution_logs.append(error_msg)
            return error_msg, "\n".join(self.execution_logs[-10:])
    
    def create_plan(self) -> tuple[str, str]:
        """Create execution plan for the current goal"""
        if not self.agent or not self.current_goal:
            return "❌ Please set a goal first", ""
        
        try:
            self.execution_logs.append(f"\n🎯 Creating execution plan...")
            
            subtasks = self.agent.plan(self.current_goal)
            
            self.execution_logs.append(f"✓ Plan created with {len(subtasks)} subtasks")
            
            plan_text = f"""✅ **Execution Plan Created**

**Goal:** {self.current_goal.description}
**Total Subtasks:** {len(subtasks)}

---

"""
            
            for i, task in enumerate(subtasks, 1):
                plan_text += f"**{i}. {task.get('name', 'Task')}**\n"
                if task.get('description'):
                    plan_text += f"   {task['description'][:200]}...\n\n"
            
            return plan_text, "\n".join(self.execution_logs[-10:])
            
        except Exception as e:
            error_msg = f"❌ Error creating plan: {str(e)}"
            self.execution_logs.append(error_msg)
            return error_msg, "\n".join(self.execution_logs[-10:])
    
    def execute_goal(self) -> tuple[str, str, str]:
        """Execute the current goal"""
        if not self.agent or not self.current_goal:
            return "❌ Please set a goal and create a plan first", "", ""
        
        try:
            self.execution_logs.append(f"\n🚀 Executing goal: {self.current_goal.id}")
            
            results = self.agent.execute(self.current_goal)
            
            self.execution_logs.append(f"✓ Execution completed")
            
            result_text = f"""✅ **Execution Completed**

**Status:** {results['status']}
**Goals Executed:** {results.get('goals_executed', 0)}

---

"""
            
            if results.get('results'):
                for result in results['results']:
                    result_text += f"### 🎯 Goal Type: {result['goal_type']}\n\n"
                    execution = result.get('execution', {})
                    
                    # Campaign Details
                    if execution.get('campaign_id'):
                        result_text += f"**Campaign ID:** `{execution['campaign_id']}`\n"
                        result_text += f"**Status:** {execution.get('status', 'N/A').upper()}\n"
                        result_text += f"**Duration:** {execution.get('duration_days', 'N/A')} days\n"
                        result_text += f"**Budget:** ${execution.get('budget', 0):,.2f}\n\n"
                    
                    # Deployment Details
                    deployment = execution.get('deployment', {})
                    if deployment:
                        result_text += f"### 📊 Deployment Metrics\n\n"
                        result_text += f"**Channels:** {', '.join(deployment.get('channels_deployed', []))}\n"
                        result_text += f"**Total Reach:** {deployment.get('total_reach', 0):,}\n\n"
                        
                        # Email metrics
                        email_data = deployment.get('email', {})
                        if email_data:
                            email_stats = email_data.get('stats', {})
                            result_text += f"#### 📧 Email Campaign\n"
                            result_text += f"- Sent: **{email_stats.get('total_sent', 0)}** emails\n"
                            result_text += f"- Opened: **{email_stats.get('opened', 0)}** ({email_stats.get('open_rate', 0)}%)\n"
                            result_text += f"- Clicked: **{email_stats.get('clicked', 0)}** ({email_stats.get('click_rate', 0)}%)\n"
                            result_text += f"- Converted: **{email_stats.get('converted', 0)}** ({email_stats.get('conversion_rate', 0)}%)\n\n"
                        
                        # Social media metrics
                        social_data = deployment.get('social_media', {})
                        if social_data:
                            social_stats = social_data.get('stats', {})
                            result_text += f"#### 📱 Social Media\n"
                            result_text += f"- Posts: **{social_stats.get('total_posts', 0)}**\n"
                            result_text += f"- Impressions: **{social_stats.get('total_impressions', 0):,}**\n"
                            result_text += f"- Likes: **{social_stats.get('total_likes', 0):,}**\n"
                            result_text += f"- Comments: **{social_stats.get('total_comments', 0):,}**\n"
                            result_text += f"- Shares: **{social_stats.get('total_shares', 0):,}**\n"
                            result_text += f"- Engagement Rate: **{social_stats.get('avg_engagement_rate', 0)}%**\n\n"
                    
                    result_text += f"**Message:** {execution.get('message', 'N/A')}\n\n"
                    
                    # Show evaluation if available
                    evaluation = result.get('evaluation', {})
                    if evaluation.get('evaluation_text'):
                        result_text += f"### 📈 AI Evaluation:\n{evaluation['evaluation_text'][:800]}...\n\n"
            
            # Generate metrics chart
            metrics_chart = self.generate_metrics_chart()
            
            return result_text, "\n".join(self.execution_logs[-15:]), metrics_chart
            
        except Exception as e:
            error_msg = f"❌ Error executing goal: {str(e)}"
            self.execution_logs.append(error_msg)
            return error_msg, "\n".join(self.execution_logs[-15:]), None
    
    def get_status_report(self) -> tuple[str, str]:
        """Get comprehensive status report"""
        if not self.agent:
            return "❌ Please initialize the agent first", None
        
        try:
            report = self.agent.get_status_report()
            
            report_text = f"""📊 **Status Report**

**Client:** {report['client_name']}
**Store Type:** {report['store_type']}

**Goals Summary:**
- Total Goals: {report['total_goals']}
- Active Goals: {report['active_goals']}
- Completed Goals: {report['completed_goals']}

---

"""
            
            if report.get('goals'):
                report_text += "### All Goals:\n\n"
                for goal in report['goals']:
                    report_text += f"**{goal['id']}**\n"
                    report_text += f"- Type: {goal['goal_type']}\n"
                    report_text += f"- Status: {goal['status']}\n"
                    report_text += f"- Target: {goal['target']}\n\n"
            
            # Generate status chart
            status_chart = self.generate_status_chart(report)
            
            return report_text, status_chart
            
        except Exception as e:
            return f"❌ Error getting status: {str(e)}", None
    
    def generate_metrics_chart(self):
        """Generate metrics visualization"""
        if not self.agent:
            return None
        
        try:
            goals = self.agent.goals
            
            # Count by status
            status_counts = {}
            for goal in goals:
                status = goal.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(status_counts.keys()),
                    y=list(status_counts.values()),
                    marker_color=['#3498db', '#f39c12', '#2ecc71', '#e74c3c']
                )
            ])
            
            fig.update_layout(
                title="Goal Status Distribution",
                xaxis_title="Status",
                yaxis_title="Count",
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error generating metrics chart: {e}")
            return None
    
    def generate_status_chart(self, report: Dict[str, Any]):
        """Generate status pie chart"""
        try:
            labels = ['Active', 'Completed', 'Pending']
            values = [
                report['active_goals'],
                report['completed_goals'],
                report['total_goals'] - report['active_goals'] - report['completed_goals']
            ]
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    marker_colors=['#f39c12', '#2ecc71', '#95a5a6']
                )
            ])
            
            fig.update_layout(
                title="Goals Overview",
                height=400
            )
            
            return fig
            
        except Exception as e:
            print(f"Error generating status chart: {e}")
            return None
    
    def chat_with_agent(self, message: str, history: List) -> List:
        """Chat interface with the agent"""
        if not history:
            history = []
            
        if not self.agent:
            history.append((message, "❌ Please initialize the agent first"))
            return history
        
        try:
            # Simple Q&A about current status
            response = ""
            
            if "status" in message.lower():
                report = self.agent.get_status_report()
                response = f"Current status: {report['active_goals']} active goals, {report['completed_goals']} completed goals."
            elif "goal" in message.lower():
                if self.current_goal:
                    response = f"Current goal: {self.current_goal.description} ({self.current_goal.status.value})"
                else:
                    response = "No current goal set."
            else:
                response = "I can help you with goal status, execution monitoring, and agent information. Try asking about 'status' or 'goals'."
            
            history.append((message, response))
            return history
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            history.append((message, error_msg))
            return history
    
    def generate_campaign_content(self) -> tuple[str, str]:
        """Generate campaign content for approval"""
        if not self.agent or not self.current_goal:
            return "❌ Please set a goal first", ""
        
        try:
            # Generate campaign content using the acquisition module
            campaign_data = self.agent.acquisition_module.create_promotion_campaign(
                target_audience="target customers",
                campaign_type=self.current_goal.goal_type.value,
                budget=5000.0,
                duration_days=30,
                store_context={
                    "name": self.agent.client_name,
                    "type": self.agent.store_type,
                    "location": self.agent.location
                }
            )
            
            # Store for approval
            self.pending_campaign = campaign_data
            self.campaign_content_draft = campaign_data.get('campaign_plan', '')
            
            content_display = f"""## 📝 Generated Campaign Content

**Campaign Type:** {campaign_data.get('campaign_type', 'N/A')}
**Budget:** ${campaign_data.get('budget', 0):,.2f}
**Duration:** {campaign_data.get('start_date', '')} to {campaign_data.get('end_date', '')}

---

### Campaign Plan:

{self.campaign_content_draft}

---

**Status:** ⏳ Pending Approval

You can:
1. **Approve** to deploy as-is
2. **Edit** the content below and regenerate
3. **Request Changes** with specific instructions
"""
            
            return content_display, self.campaign_content_draft
            
        except Exception as e:
            return f"❌ Error generating campaign: {str(e)}", ""
    
    def regenerate_campaign_content(self, user_instructions: str, current_content: str) -> tuple[str, str]:
        """Regenerate campaign content based on user feedback"""
        if not self.agent:
            return "❌ Please initialize the agent first", current_content
        
        try:
            from langchain_core.prompts import ChatPromptTemplate
            
            # Use LLM to revise the campaign based on user instructions
            revision_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an expert retail marketing content editor. Revise the marketing campaign based on user feedback."),
                ("user", """Original Campaign Content:
{original_content}

User Instructions for Changes:
{user_instructions}

Please revise the campaign content according to the user's instructions while maintaining professional marketing standards and the original campaign structure.""")
            ])
            
            chain = revision_prompt | self.agent.llm
            
            response = chain.invoke({
                "original_content": current_content,
                "user_instructions": user_instructions
            })
            
            revised_content = response.content if hasattr(response, 'content') else str(response)
            
            # Update stored content
            self.campaign_content_draft = revised_content
            if self.pending_campaign:
                self.pending_campaign['campaign_plan'] = revised_content
            
            content_display = f"""## 📝 Revised Campaign Content

**Changes Applied:** {user_instructions[:100]}...

---

### Updated Campaign Plan:

{revised_content}

---

**Status:** ⏳ Pending Approval (Revised)
"""
            
            return content_display, revised_content
            
        except Exception as e:
            return f"❌ Error regenerating: {str(e)}", current_content
    
    def approve_and_deploy_campaign(self, approved_content: str) -> str:
        """Approve and deploy the campaign with the approved content"""
        if not self.agent or not self.current_goal:
            return "❌ Please set a goal first"
        
        try:
            # Update the campaign content with approved version
            if self.pending_campaign:
                self.pending_campaign['campaign_plan'] = approved_content
            else:
                self.pending_campaign = {'campaign_plan': approved_content, 'campaign_type': 'approved'}
            
            # Now execute the goal with approved content
            self.current_goal.update_status(GoalStatus.IN_PROGRESS)
            
            # Execute with approved content
            execution_result = self.agent._execute_customer_acquisition(self.current_goal)
            
            self.current_goal.update_status(GoalStatus.COMPLETED)
            self.current_goal.add_result("execution", execution_result)
            
            # Clear pending campaign
            self.pending_campaign = None
            self.campaign_content_draft = ""
            
            return f"""✅ **Campaign Approved and Deployed!**

**Campaign ID:** {execution_result.get('campaign_id', 'N/A')}
**Status:** {execution_result.get('status', 'N/A').upper()}

**Deployment Summary:**
- Channels: {', '.join(execution_result.get('channels_deployed', []))}
- Total Reach: {execution_result.get('deployment', {}).get('total_reach', 0):,}

**Next Steps:**
- Go to Tab 6 (📧 Email Campaigns) to see sent emails
- Go to Tab 7 (📱 Social Media) to see posts and comments
- Monitor performance in the Metrics tab
"""
            
        except Exception as e:
            return f"❌ Error deploying campaign: {str(e)}"
    
    def get_customer_stats(self) -> str:
        """Get customer database statistics"""
        if not self.agent:
            return "❌ Please initialize the agent first"
        
        try:
            stats = self.agent.deployment_service.get_customer_stats()
            
            output = f"""## 👥 Customer Database
            
**Total Customers:** {stats['total_customers']}
**Email Opt-in:** {stats['email_opt_in']} ({stats['email_opt_in']/stats['total_customers']*100:.1f}%)
**SMS Opt-in:** {stats['sms_opt_in']}
**Total Revenue:** ${stats['total_revenue']:,.2f}
**Average Spent:** ${stats['average_spent']:.2f}

### Customer Segments:
- **New Customers:** {stats['by_segment']['new']}
- **Occasional Shoppers:** {stats['by_segment']['occasional']}
- **Frequent Customers:** {stats['by_segment']['frequent']}
- **VIP Customers:** {stats['by_segment']['vip']}
"""
            return output
        except Exception as e:
            return f"❌ Error getting customer stats: {str(e)}"
    
    def get_sent_emails(self) -> str:
        """Get list of sent emails"""
        if not self.agent:
            return "❌ Please initialize the agent first"
        
        try:
            emails = self.agent.get_all_emails()
            
            if not emails:
                return "📭 No emails sent yet. Execute a campaign to see emails here."
            
            output = f"## 📧 Sent Emails ({len(emails)} total)\n\n"
            
            # Show most recent 20 emails
            for email in emails[:20]:
                status_icons = []
                if email['opened']:
                    status_icons.append("✅ Opened")
                if email['clicked']:
                    status_icons.append("🔗 Clicked")
                if email['converted']:
                    status_icons.append("💰 Converted")
                
                status = " | ".join(status_icons) if status_icons else "📨 Sent"
                
                # Truncate content for display
                content_preview = email['content'][:200] + "..." if len(email['content']) > 200 else email['content']
                
                output += f"""---
**To:** {email['to_name']} ({email['to_email']})
**Subject:** {email['subject']}
**Sent:** {email['sent_at'][:19]}
**Status:** {status}
**Campaign:** {email['campaign_id']}

**Email Content:**
```
{content_preview}
```

"""
            
            return output
        except Exception as e:
            return f"❌ Error getting emails: {str(e)}"
    
    def get_social_posts(self) -> str:
        """Get list of social media posts"""
        if not self.agent:
            return "❌ Please initialize the agent first"
        
        try:
            posts = self.agent.get_all_social_posts()
            
            if not posts:
                return "📱 No social posts yet. Execute a campaign to see posts here."
            
            output = f"## 📱 Social Media Posts ({len(posts)} total)\n\n"
            
            # Show most recent 20 posts
            for post in posts[:20]:
                platform_emoji = {
                    "facebook": "👥",
                    "instagram": "📸",
                    "twitter": "🐦"
                }.get(post['platform'], "📱")
                
                output += f"""---
{platform_emoji} **{post['platform'].upper()}** - Posted: {post['posted_at'][:19]}

**Post Content:**
> {post['content']}

**Hashtags:** {' '.join(post['hashtags'])}

{f"**Image:** {post['image_url']}" if post.get('image_url') else ''}

**Engagement Metrics:**
- 👁️ Impressions: {post['impressions']:,}
- ❤️ Likes: {post['likes']:,}
- 💬 Comments: {post['comments']:,}
- 🔄 Shares: {post['shares']:,}
- 🔗 Clicks: {post['clicks']:,}
- 📊 Engagement Rate: {post['engagement_rate']}%

"""
                
                # Get and display comments for this post
                comments = self.agent.deployment_service.social_service.get_post_comments(post['id'])
                if comments:
                    output += f"**💬 Comments ({len(comments)}):**\n"
                    for comment in comments[:5]:  # Show first 5 comments per post
                        sentiment_emoji = {"positive": "😊", "neutral": "😐", "negative": "😞"}.get(comment.sentiment, "💬")
                        output += f"  {sentiment_emoji} **{comment.author_name}**: {comment.content}\n"
                    if len(comments) > 5:
                        output += f"  ... and {len(comments) - 5} more comments\n"
                
                output += f"\n**Campaign:** {post['campaign_id']}\n\n"
            
            return output
        except Exception as e:
            return f"❌ Error getting social posts: {str(e)}"
    
    def get_social_comments_sample(self) -> str:
        """Get sample comments from social media posts"""
        if not self.agent:
            return "❌ Please initialize the agent first"
        
        try:
            posts = self.agent.get_all_social_posts()
            
            if not posts:
                return "💬 No posts with comments yet."
            
            output = f"## 💬 Social Media Comments Sample\n\n"
            
            # Show comments from first 5 posts
            for post in posts[:5]:
                comments = self.agent.deployment_service.social_service.get_post_comments(post['id'])
                
                if comments:
                    platform_emoji = {"facebook": "👥", "instagram": "📸", "twitter": "🐦"}.get(post['platform'], "📱")
                    output += f"""---
### {platform_emoji} {post['platform'].upper()} Post
**Content:** {post['content'][:100]}...

**Comments ({len(comments)}):**
"""
                    for comment in comments[:5]:  # Show first 5 comments
                        sentiment_emoji = {"positive": "😊", "neutral": "😐", "negative": "😞"}.get(comment.sentiment, "💬")
                        output += f"- {sentiment_emoji} **{comment.author_name}**: {comment.content}\n"
                    
                    output += "\n"
            
            return output if "Comments" in output else "💬 No comments available yet."
        except Exception as e:
            return f"❌ Error getting comments: {str(e)}"


def create_interface():
    """Create the Gradio interface"""
    ui = MarketingAgentUI()
    
    with gr.Blocks(title="Retail Marketing Agent Dashboard") as app:
        gr.Markdown("""
        # 🛍️ Retail Marketing Agent Dashboard
        
        AI-powered marketing agent for retail businesses with goal-based planning and execution
        """)
        
        with gr.Tabs():
            # Tab 1: Agent Setup
            with gr.Tab("🔧 Agent Setup"):
                gr.Markdown("### Initialize Your Marketing Agent")
                
                with gr.Row():
                    with gr.Column():
                        client_name = gr.Textbox(
                            label="Store Name",
                            placeholder="Fashion Forward Boutique",
                            value="Fashion Forward Boutique"
                        )
                        store_type = gr.Dropdown(
                            label="Store Type",
                            choices=["fashion", "electronics", "grocery", "home_goods", "beauty", "sports", "general"],
                            value="fashion"
                        )
                    with gr.Column():
                        location = gr.Textbox(
                            label="Location",
                            placeholder="Downtown Seattle",
                            value="Downtown Seattle"
                        )
                        has_online = gr.Checkbox(label="Has Online Store", value=True)
                
                init_btn = gr.Button("Initialize Agent", variant="primary")
                init_output = gr.Markdown()
                
                init_btn.click(
                    fn=ui.initialize_agent,
                    inputs=[client_name, store_type, has_online, location],
                    outputs=init_output
                )
            
            # Tab 2: Goal Setting
            with gr.Tab("🎯 Goal Setting"):
                gr.Markdown("### Set Marketing Goals")
                
                with gr.Row():
                    with gr.Column():
                        goal_type = gr.Dropdown(
                            label="Goal Type",
                            choices=[
                                "Customer Acquisition",
                                "Customer Retention",
                                "Instore Marketing",
                                "Digital Presence",
                                "Seasonal Campaign",
                                "Analytics Insights",
                                "Community Engagement"
                            ],
                            value="Customer Acquisition"
                        )
                        target = gr.Textbox(
                            label="Target",
                            placeholder="Increase foot traffic by 25%",
                            value="Increase foot traffic by 25% and acquire 500 new customers"
                        )
                        timeframe = gr.Textbox(
                            label="Timeframe",
                            placeholder="30 days",
                            value="30 days"
                        )
                    
                    with gr.Column():
                        description = gr.Textbox(
                            label="Description",
                            placeholder="Holiday season customer acquisition campaign",
                            value="Holiday season customer acquisition campaign",
                            lines=3
                        )
                        priority = gr.Slider(
                            label="Priority",
                            minimum=1,
                            maximum=5,
                            value=1,
                            step=1
                        )
                
                set_goal_btn = gr.Button("Set Goal", variant="primary")
                goal_output = gr.Markdown()
                goal_logs = gr.Textbox(label="Execution Logs", lines=5)
                
                set_goal_btn.click(
                    fn=ui.set_goal,
                    inputs=[goal_type, target, timeframe, description, priority],
                    outputs=[goal_output, goal_logs]
                )
            
            # Tab 3: Campaign Content Approval
            with gr.Tab("✅ Campaign Approval"):
                gr.Markdown("""### Review & Approve Marketing Content
                
Generate campaign content, review it, request changes, and approve before deployment.""")
                
                generate_content_btn = gr.Button("🎨 Generate Campaign Content", variant="primary")
                
                campaign_preview = gr.Markdown()
                
                gr.Markdown("### Edit Campaign Content")
                campaign_content_editor = gr.Textbox(
                    label="Campaign Content",
                    placeholder="Generated content will appear here for editing...",
                    lines=15
                )
                
                with gr.Row():
                    with gr.Column():
                        change_instructions = gr.Textbox(
                            label="Request Changes (Optional)",
                            placeholder="E.g., 'Make it more exciting', 'Add a holiday theme', 'Focus more on discounts'",
                            lines=3
                        )
                        regenerate_btn = gr.Button("🔄 Regenerate with Changes", variant="secondary")
                    
                    with gr.Column():
                        approve_btn = gr.Button("✅ Approve & Deploy Campaign", variant="primary", size="lg")
                        approval_output = gr.Markdown()
                
                # Connect buttons
                generate_content_btn.click(
                    fn=ui.generate_campaign_content,
                    outputs=[campaign_preview, campaign_content_editor]
                )
                
                regenerate_btn.click(
                    fn=ui.regenerate_campaign_content,
                    inputs=[change_instructions, campaign_content_editor],
                    outputs=[campaign_preview, campaign_content_editor]
                )
                
                approve_btn.click(
                    fn=ui.approve_and_deploy_campaign,
                    inputs=[campaign_content_editor],
                    outputs=approval_output
                )
            
            # Tab 4: Execution & Monitoring
            with gr.Tab("🚀 Execution & Monitoring"):
                gr.Markdown("### Create Plan and Execute")
                
                with gr.Row():
                    plan_btn = gr.Button("Create Execution Plan", variant="secondary")
                    execute_btn = gr.Button("Execute Goal", variant="primary")
                
                plan_output = gr.Markdown()
                execution_logs = gr.Textbox(label="Real-time Logs", lines=10)
                
                with gr.Row():
                    execution_output = gr.Markdown()
                
                metrics_plot = gr.Plot(label="Execution Metrics")
                
                plan_btn.click(
                    fn=ui.create_plan,
                    outputs=[plan_output, execution_logs]
                )
                
                execute_btn.click(
                    fn=ui.execute_goal,
                    outputs=[execution_output, execution_logs, metrics_plot]
                )
            
            # Tab 5: Metrics Dashboard
            with gr.Tab("📊 Metrics & Analytics"):
                gr.Markdown("### Performance Dashboard")
                
                refresh_btn = gr.Button("Refresh Status", variant="secondary")
                
                with gr.Row():
                    status_output = gr.Markdown()
                
                status_chart = gr.Plot(label="Goals Overview")
                
                refresh_btn.click(
                    fn=ui.get_status_report,
                    outputs=[status_output, status_chart]
                )
            
            # Tab 6: Customer Database
            with gr.Tab("👥 Customer Database"):
                gr.Markdown("### Mock Customer Database (500 customers)")
                
                customer_stats_output = gr.Markdown()
                customer_refresh_btn = gr.Button("Refresh Customer Stats", variant="secondary")
                
                customer_refresh_btn.click(
                    fn=ui.get_customer_stats,
                    outputs=customer_stats_output
                )
            
            # Tab 7: Sent Emails
            with gr.Tab("📧 Email Campaigns"):
                gr.Markdown("### All Sent Emails with Engagement Tracking")
                
                emails_output = gr.Markdown()
                emails_refresh_btn = gr.Button("Refresh Emails", variant="secondary")
                
                emails_refresh_btn.click(
                    fn=ui.get_sent_emails,
                    outputs=emails_output
                )
            
            # Tab 8: Social Media Posts
            with gr.Tab("📱 Social Media"):
                gr.Markdown("### All Social Media Posts with Comments & Engagement")
                
                social_output = gr.Markdown()
                social_refresh_btn = gr.Button("Refresh Posts", variant="secondary")
                
                social_refresh_btn.click(
                    fn=ui.get_social_posts,
                    outputs=social_output
                )
            
            # Tab 9: Chat Interface
            with gr.Tab("💬 Chat with Agent"):
                gr.Markdown("### Ask Questions About Your Campaigns")
                
                chatbot = gr.Chatbot(height=400)
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Ask about status, goals, or execution..."
                )
                clear_btn = gr.Button("Clear Chat")
                
                def submit_message(message, history):
                    if not message.strip():
                        return history
                    return ui.chat_with_agent(message, history)
                
                msg.submit(
                    fn=submit_message,
                    inputs=[msg, chatbot],
                    outputs=chatbot
                ).then(lambda: "", None, msg)
                
                clear_btn.click(lambda: [], None, chatbot)
        
        gr.Markdown("""
        ---
        ### 📖 Quick Guide
        1. **Setup**: Initialize your agent with store details
        2. **Goal**: Set a marketing goal with target and timeframe
        3. **Plan**: Let AI create an execution plan
        4. **Execute**: Run the campaign and monitor progress
        5. **Track**: View metrics and chat with the agent
        """)
    
    return app


if __name__ == "__main__":
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,  # Enable public URL sharing
        show_error=True,
        theme=gr.themes.Soft()
    )
