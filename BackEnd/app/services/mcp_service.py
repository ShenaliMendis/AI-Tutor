import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
import json

class LangChainAgent:
    def __init__(self):
        """Initialize the LangChain agent."""
        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", 
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    async def get_response(self, message):
        """Get a response from the LangChain agent."""
        # Connect to the MCP clients
        async with MultiServerMCPClient(self.get_mcp_server_config()) as client:
            # Create the agent with available tools
            agent = create_react_agent(self.model, client.get_tools())
            
            # Create formatted input for the agent
            formatted_input = {"messages": [{"type": "human", "content": message}]}
            
            # Invoke the agent with the message
            response = await agent.ainvoke(formatted_input)
            
            response = response["messages"][-1].content
            
            # print("LangChain Response:", response)
            
            # Return the full response
            return response
    
    @staticmethod
    def get_mcp_server_config():
        """Get the MCP server configuration from JSON file."""
        
        # Get the absolute path to the config file
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'mcp_servers', 'mcp.json')
        
        # Load the configuration from the JSON file
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        return config
