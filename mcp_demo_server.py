"""
MCP Server Demo
暴露两个简单工具给外部Agent调用
"""
from mcp.server.fastmcp import FastMCP

# 创建 MCP Server 实例
mcp = FastMCP("demo-server")



# ============ 工具 1: greet ============
@mcp.tool() # 装饰器，把一个普通python函数注册为MCP工具
def greet(name:str) -> str:
    """
    向某人问好
    
    参数:
        name: 要问候的人的名字
    
    返回:
        一句问候语
    """
    print(f"[Server] greet 被调用，name={name}")
    return f"Hello, {name}! 来自 MCP Server 的问候。"

# ============ 工具 2: add ============
@mcp.tool()
def add(a:int,b:int) -> int:
    """
    计算两个整数的和
    
    参数:
        a: 第一个整数
        b: 第二个整数
    
    返回:
        两数之和
    """
    print(f"[Server] add 被调用，a={a}, b={b}")
    return a+b


# ============ 启动 Server ============
if __name__ == "__main__":
    print("MCP Demo Server 启动中...")
    mcp.run(transport="stdio")
    # stdio 模式：通过标准输入输出通信
    # 还有多种通信方式：stdio/SSE/HTTP