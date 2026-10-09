from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, START, END
import asyncio
import json
from src.config.settings import settings
from src.llm.ollama_client import OllamaProvider
from src.memory.memory_manager import MemoryManager
from src.tools import registry, ToolManager

class AgentState(TypedDict):
    messages: List[dict]

class UNEXAgent:
    def __init__(self):
        self.llm_provider = OllamaProvider(default_model=settings.llm_model)
        self.memory_manager = MemoryManager(self.llm_provider)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Define the nodes
        workflow.add_node("agent", self._call_agent)
        
        # Define edges
        workflow.add_edge(START, "agent")
        workflow.add_edge("agent", END)
        
        return workflow.compile()

    async def _call_agent(self, state: AgentState):
        messages = state['messages']
        
        # Enforce Short-Term Memory Limit (last 20 interactions = 40 messages approx + system)
        if len(messages) > 41:
            messages = [messages[0]] + messages[-40:]
            
        user_query = messages[-1].get("content", "")
        
        # Retrieve Long-Term Memory context
        context_str = self.memory_manager.get_context_for_query(user_query)
        
        # Prepend system prompt if not present
        if not any(m.get("role") == "system" for m in messages):
            base_system = "You are UNEX, a futuristic personal operating system. You are minimal, modern, and professional. Always use the default greeting: 'Hello Prajeeth, UNEX is ready.' when initially starting a conversation."
            system_msg = {
                "role": "system", 
                "content": f"{base_system}\n\n{context_str}"
            }
            messages.insert(0, system_msg)
        else:
            # Update existing system prompt with new context
            for m in messages:
                if m.get("role") == "system":
                    base_system = m.get("content").split("Relevant Memories:")[0].strip()
                    if context_str:
                        m["content"] = f"{base_system}\n\n{context_str}"
                    break
            
        # Tool Loop
        max_tool_iterations = 3
        for i in range(max_tool_iterations):
            tools_schema = registry.get_tools_schema()
            response = await self.llm_provider.agenerate_chat(messages, tools=tools_schema)
            
            # Check for tool calls
            tool_calls = ToolManager.parse_tool_calls(response)
            if not tool_calls:
                break
                
            # Execute tool calls
            messages.append({"role": "assistant", "content": response})
            for tool_name, tool_args in tool_calls:
                result = await ToolManager.execute_tool(tool_name, tool_args)
                result_str = json.dumps(result.dict()) if hasattr(result, 'dict') else str(result)
                messages.append({"role": "tool", "name": tool_name, "content": result_str})
                
        # If we broke out of the loop because of no tool calls, response is the final text
        # But if we executed tools, the loop ends after appending tool responses. 
        # We need to generate a final response summarizing the tool results if the loop hit max iterations
        # or if the last message is a tool response.
        if messages[-1]["role"] == "tool":
            response = await self.llm_provider.agenerate_chat(messages)
        
        # Asynchronously extract memories without blocking the response
        asyncio.create_task(self.memory_manager.process_interaction(user_query, response))
        
        # Append the assistant's response to the state
        messages.append({"role": "assistant", "content": response})
        return {"messages": messages}

    async def chat(self, user_input: str, history: List[dict] = None) -> str:
        """Main entry point for chat interaction."""
        if history is None:
            history = []
            
        history.append({"role": "user", "content": user_input})
        
        initial_state = {"messages": history}
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        # Return the last message content
        return final_state["messages"][-1]["content"]
