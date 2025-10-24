import asyncio, sys
from mcp import ClientSession, StdioServerParameters # type: ignore
from mcp.client.stdio import stdio_client # type: ignore

async def main():
    city = sys.argv[1] if len(sys.argv) > 1 else "Montevideo"
    params = StdioServerParameters(command=sys.executable, args=["server.py"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool("get_weather", {"city": city})
            for c in res.content:
                if getattr(c, "data", None) is not None:
                    print(c.data)
                elif getattr(c, "text", None):
                    print(c.text)

if __name__ == "__main__":
    asyncio.run(main())
