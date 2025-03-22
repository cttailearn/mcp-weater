import json
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")

# 天气查询api配置
WEATHER_API_URL = "https://restapi.amap.com/v3/weather/weatherInfo?"
WEATHER_API_KEY = "16f6ef45d6a0565d84ee44e9a0a67e2e"
USER_AGENT = "weather-app/1.0"

async def get_weather_data(city: str) -> dict[str, Any] | None:
    """
    从高德天气查询API获取天气数据
    :param city: 城市中文名称
    :return: 天气数据字典，如果查询失败则返回None
    """
    print(city)
    print(WEATHER_API_URL)
    print(WEATHER_API_KEY)

    params = {"city": city, "key": WEATHER_API_KEY}
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(WEATHER_API_URL, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}

def format_weather_data(data: dict[str,Any] | str) -> str:
    """
    将天气数据格式化为文本。
    :param data: 天气数据json
    :return: 格式化后的天气数据文本
    """
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            return f"JSON解析错误: {str(e)}"
        except Exception as e:
            return f"解析失败: {str(e)}"
    
    if "error" in data:
        return f"错误: {data['error']}"
    
    live_data = data['lives'][0]

    # 获取具体字段
    province = live_data['province']
    city = live_data['city']
    weather = live_data['weather']
    temperature = live_data['temperature']
    wind = f"{live_data['winddirection']}风 {live_data['windpower']}级"
    report_time = live_data['reporttime']

    return (f"""
        省份: {province}
        城市: {city}
        天气: {weather}
        温度: {temperature}℃
        风力: {wind}
        报告时间: {report_time}
        """)

@mcp.tool()
async def query_weater(city: str) -> str:
    """
    输入指定城市的中文名称，返回今日的天气情况。
    :param city: 城市名称
    :return: 格式化后的天气情况
    """
    data = await get_weather_data(city)
    return format_weather_data(data)

if __name__ == "__main__":
    # 以stdio 方式运行
    mcp.run(transport='stdio')

