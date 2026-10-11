import inspect
import json
import time
from typing import Callable, Dict, Any, Optional, List
from pydantic import BaseModel, ValidationError
from backend.app.core.logging import app_logger


class MCPToolMetadata(BaseModel):
    name: str
    server: str
    description: str
    parameters_schema: Dict[str, Any]
    read_only: bool = True


class MCPRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, MCPToolMetadata] = {}

    def register_tool(
        self,
        name: str,
        server: str,
        description: str,
        func: Callable,
        param_model: Optional[type[BaseModel]] = None,
        read_only: bool = True
    ):
        """Registers an MCP tool with schema, safety policy, and validation."""
        schema = param_model.model_json_schema() if param_model else {}
        self._tools[name] = (func, param_model)
        self._metadata[name] = MCPToolMetadata(
            name=name,
            server=server,
            description=description,
            parameters_schema=schema,
            read_only=read_only
        )
        app_logger.debug(f"Registered MCP tool: {server}.{name} (Read-Only: {read_only})")

    def list_tools(self) -> List[MCPToolMetadata]:
        return list(self._metadata.values())

    def get_tool_metadata(self, name: str) -> Optional[MCPToolMetadata]:
        return self._metadata.get(name)

    def execute_tool(self, name: str, params: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes an MCP tool with strict input validation, logging, and error handling."""
        start_time = time.time()
        if name not in self._tools:
            return {
                "success": False,
                "error": f"Tool '{name}' is not registered in the MCP catalog.",
                "duration_ms": 0.0
            }

        func, param_model = self._tools[name]
        meta = self._metadata[name]

        try:
            # 1. Validate inputs via Pydantic model if registered
            if param_model:
                validated_params = param_model(**params)
                call_args = validated_params.model_dump()
            else:
                call_args = params

            # 2. Inject user_context if expected
            sig = inspect.signature(func)
            if "user_context" in sig.parameters:
                call_args["user_context"] = user_context

            # 3. Safe Execution
            result = func(**call_args)
            duration_ms = (time.time() - start_time) * 1000

            app_logger.info(f"MCP Tool Executed: {meta.server}.{name} in {duration_ms:.2f}ms")
            return {
                "success": True,
                "tool": name,
                "server": meta.server,
                "result": result,
                "duration_ms": round(duration_ms, 2)
            }

        except ValidationError as val_err:
            duration_ms = (time.time() - start_time) * 1000
            app_logger.warning(f"MCP Tool validation error on {name}: {val_err}")
            return {
                "success": False,
                "tool": name,
                "error": f"Invalid tool arguments: {str(val_err)}",
                "duration_ms": round(duration_ms, 2)
            }
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            app_logger.error(f"MCP Tool execution error on {name}: {exc}")
            return {
                "success": False,
                "tool": name,
                "error": f"Tool execution failed: {str(exc)}",
                "duration_ms": round(duration_ms, 2)
            }


# Global Registry Instance
mcp_registry = MCPRegistry()


def get_mcp_registry() -> MCPRegistry:
    return mcp_registry
