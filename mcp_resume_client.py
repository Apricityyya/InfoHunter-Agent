"""
MCP Client 演示：完整调用 4 个工具
模拟外部系统通过 MCP 协议使用简历评估服务
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_resume_server.py"],
    )
    
    test_resume = """
    王莹，同济大学计算机科学与技术专业本科在读。
    技能：掌握 Python、了解 C++ 基础语法；熟悉 RAG、Agent、Function Calling、MCP 等大模型应用范式。
    项目：
    - InfoHunter：基于 RAG+Agent 的智能信息追踪系统，部署到阿里云 ECS。
    - EcoAgent：复现 AAAI 2026 论文，云-端协同 Agent 框架。
    """
    
    test_jd = """
    岗位：AI Agent 开发实习生
    职责：参与 AI Agent 系统的设计与研发；推动 Agent 在业务场景的落地。
    要求：熟悉 Python，有 LangChain / LangGraph 使用经验；了解 RAG、Function Calling、MCP 等技术。
    """
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("=" * 60)
            print("MCP Resume Server 端到端演示")
            print("=" * 60)
            
            # 列出工具
            tools = await session.list_tools()
            print(f"\n[已发现 {len(tools.tools)} 个工具]")
            for t in tools.tools:
                print(f"  - {t.name}")
            
            # Step 1: 解析简历
            print("\n--- Step 1: 解析简历 ---")
            r1 = await session.call_tool("parse_resume", {"resume_text": test_resume})
            resume_info = json.loads(r1.content[0].text)
            print(f"提取技能: {resume_info.get('skills', [])}")
            
            # Step 2: 解析 JD
            print("\n--- Step 2: 解析 JD ---")
            r2 = await session.call_tool("parse_jd", {"jd_text": test_jd})
            jd_info = json.loads(r2.content[0].text)
            print(f"必需技能: {jd_info.get('required_skills', [])}")
            
            # Step 3: 计算匹配度
            print("\n--- Step 3: 计算匹配度 ---")
            r3 = await session.call_tool("compute_match_score", {
                "resume_info": resume_info,
                "jd_info": jd_info,
            })
            score_info = json.loads(r3.content[0].text)
            print(f"综合评分: {score_info.get('overall_score', 0)}/100")
            
            # Step 4: 生成报告
            print("\n--- Step 4: 生成改进报告 ---")
            r4 = await session.call_tool("generate_gap_report", {
                "resume_info": resume_info,
                "jd_info": jd_info,
                "score_info": score_info,
            })
            report = r4.content[0].text
            print(f"\n{report[:500]}...")
            
            print("\n" + "=" * 60)
            print("✅ 端到端调用成功！")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())