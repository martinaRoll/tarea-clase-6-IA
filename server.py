from mcp.server.fastmcp import FastMCP # type: ignore
import requests

mcp = FastMCP("WeatherMCP")

@mcp.tool()
def get_weather(city: str) -> dict:

    geo = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                       params={"name": city, "count": 1}).json()
    if not geo.get("results"):
        return {"error": "Ciudad no encontrada"}

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    weather = requests.get("https://api.open-meteo.com/v1/forecast",
                           params={
                               "latitude": lat,
                               "longitude": lon,
                               "current": "temperature_2m,wind_speed_10m",
                           }).json()

    cur = weather.get("current", {})
    return {
        "city": city,
        "temperature_c": cur.get("temperature_2m"),
        "wind_speed_mps": cur.get("wind_speed_10m"),
        "source": "open-meteo.com"
    }


if __name__ == "__main__":
    mcp.run()
