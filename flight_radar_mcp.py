#!/usr/bin/env python3
"""
Flight Radar MCP Server

An MCP server that provides access to ADS-B flight data through the Flight Radar API.
"""

import json, os, signal, sys
from typing import Any, Dict, Optional
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

FLIGHTRADAR_API_BASE_URL = os.environ["FLIGHTRADAR_API_BASE_URL"]
print(f"Using Flight Radar API base URL: {FLIGHTRADAR_API_BASE_URL}")

# Initialize FastMCP server
mcp = FastMCP(name="Flight Radar", 
              instructions="""This server provides live data of aircraft positions and flight information as well as routes."""
              )

# HTTP client for making API requests
http_client = httpx.AsyncClient(timeout=30.0)


async def make_api_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Make a request to the Flight Radar API."""
    url = f"{FLIGHTRADAR_API_BASE_URL}{endpoint}"
    try:
        response = await http_client.get(url, params=params or {})
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise Exception(f"API request failed: {e}")


@mcp.tool()
async def get_meta_info() -> str:
    """Get meta information about the Flight Radar API."""
    try:
        result = await make_api_request("/api/v1/info")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting meta info: {str(e)}"


@mcp.tool()
async def get_current_flights() -> str:
    """
    Get a list of all current flights.
    
    Returns an array of flight objects with:
    - id: Unique flight identifier
    - icao24: ICAO 24-Bit hex address  
    - cls: callsign
    - lstCntct: time of last contact
    - firstCntct: time of first contact
    
    Example response:
    [
      {
        "id": "683f570bd570101935e7ff63",
        "icao24": "394a03", 
        "cls": "AFR990",
        "lstCntct": "2025-06-03T20:12:03.615000Z",
        "firstCntct": "2025-06-03T20:11:55.542000Z"
      }
    ]
    """
    try:
        result = await make_api_request("/api/v1/flights")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting flights: {str(e)}"


@mcp.tool()
async def get_military_flights() -> str:
    """Get a list of current military flights only."""
    try:
        result = await make_api_request("/api/v1/flights", {"filter": "mil"})
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting military flights: {str(e)}"


@mcp.tool()
async def get_current_aircraft_positions() -> str:
    """
    Get the current position of all aircraft currently tracked by the Flight Radar API.
    
    Returns a map with ICAO24 hex address as key and arrays of [lat, lon, alt] coordinates as values.
    
    Example response:
    {
      "300781": [
        [47.669632, 11.054512, 28200],
        [47.655716, 11.048882, 28475]
      ]
    }
    """
    try:
        result = await make_api_request("/api/v1/positions")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting all positions: {str(e)}"

@mcp.tool()
async def get_flight_by_id(flight_id: str) -> str:
    """
    Get detailed information about a specific flight.
    
    Args:
        flight_id: The unique identifier of the flight
    
    Example response:
    {
      "id": "683f570bd570101935e7ff63",
      "icao24": "394a03",
      "cls": "AFR990", 
      "lstCntct": "2025-06-03T20:14:19.571000Z",
      "firstCntct": "2025-06-03T20:11:55.542000Z"
    }
    
    Fields:
    - icao24: ICAO 24-Bit hex address
    - cls: callsign
    - lstCntct: time of last contact
    - firstCntct: time of first contact
    """
    try:
        result = await make_api_request(f"/api/v1/flights/{flight_id}")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting flight {flight_id}: {str(e)}"


@mcp.tool()
async def get_flight_positions(flight_id: str) -> str:
    """
    Get position data for a specific flight.
    
    Args:
        flight_id: The unique identifier of the flight
    
    Returns an array of [lat, lon, alt] coordinates:
    [
      [47.520152, 7.920509, 32025],
      [47.655716, 11.048882, 28475]
    ]
    """
    try:
        result = await make_api_request(f"/api/v1/flights/{flight_id}/positions")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting positions for flight {flight_id}: {str(e)}"


@mcp.tool()
async def get_aircraft_info(icao24addr: str) -> str:
    """
    Get aircraft information by ICAO 24-bit address.
    
    Args:
        icao24addr: The ICAO 24-bit address of the aircraft (e.g., 'a1b2c3')
    
    Example response:
    {
      "icao24": "345314",
      "reg": "EC-MOO",
      "icaoType": "A321", 
      "type": "Airbus A321 231SL",
      "op": "Vueling Airlines"
    }
    
    Fields:
    - icao24: ICAO 24-bit hex address
    - reg: Registration
    - icaoType: ICAO aircraft type code
    - type: Full aircraft type description
    - op: Operator/Airline name
    """
    try:
        result = await make_api_request(f"/api/v1/aircraft/{icao24addr}")
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error getting aircraft {icao24addr}: {str(e)}"


@mcp.tool()
async def search_flights(filter_type: Optional[str] = None, limit: Optional[int] = None) -> str:
    """
    Search flights with optional filtering and limiting.
    
    Args:
        filter_type: Filter flights (e.g. 'mil' for military only)
        limit: Maximum number of flights to return
    """
    try:
        params = {}
        if filter_type:
            params["filter"] = filter_type
        if limit:
            params["limit"] = limit
        
        result = await make_api_request("/api/v1/flights", params)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error searching flights: {str(e)}"


@mcp.tool()
async def get_flight_route(callsign: str) -> str:
    """
    Get the route (departure and destination airports) for a flight by callsign.
    
    Args:
        callsign: The flight callsign (e.g., 'SWR282', 'AFR990')
    
    Example response:
    {
      "flight": "SWR282",
      "route": "ZRH-JNB",
      "updatetime": 1747593022
    }
    
    Fields:
    - flight: The flight callsign
    - route: Departure airport and destination airport separated by dash (IATA codes)
    - updatetime: Unix timestamp of last update
    """
    try:
        url = f"https://hexdb.io/api/v1/route/iata/{callsign}"
        response = await http_client.get(url)
        response.raise_for_status()
        result = response.json()
        return json.dumps(result, indent=2)
    except httpx.HTTPError as e:
        return f"Error getting route for flight {callsign}: {str(e)}"
    except Exception as e:
        return f"Error getting route for flight {callsign}: {str(e)}"


def signal_handler(signum, frame):
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    mcp.run()