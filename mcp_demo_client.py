"""
MCP Client Demo
连接到 mcp_demo_server.py 并调用它的工具
"""

import asyncio
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # ============ 配置：怎么启动 Server ============
    # Client 会通过这个配置去拉起 Server 进程
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_demo_server.py"],
    )

    # ============ 启动 Server + 建立连接 ============
    async with stdio_client(server_params) as (read,write):
        async with ClientSession(read,write) as session:
            # 初始化连接
            await session.initialize()
            print("=" * 50)
            print("MCP Client 已连接到 Server")
            print("=" * 50)

            # ============ 列出 Server 暴露的所有工具 ============
            tools = await session.list_tools()
            print(f"\n可用工具列表:")
            for tool in tools.tools:
                print(f" - {tool.name}: {tool.description}")

            # ============ 调用工具 1: greet ============
            print("\n" + "=" * 50)
            print("调用 greet")
            print("=" * 50)
            result = await session.call_tool("greet",{"name":"王莹"})
            print(f"返回: {result.content[0].text}")

            # ============ 调用工具 2: add ============
            print("\n" + "=" * 50)
            print("调用 add")
            print("=" * 50)
            result = await session.call_tool("add",{"a":3,"b":5})
            print(f"返回: {result.content[0].text}")



if __name__=="__main__":
    asyncio.run(main())