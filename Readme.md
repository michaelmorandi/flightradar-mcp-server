# Flight Radar MCP Server

An MCP (Model Context Protocol) server that provides access to ADS-B flight data through the Flight Radar API.

## Features

This MCP server provides the following tools:

- **get_meta_info**: Get meta information about the Flight Radar API
- **check_api_status**: Check if the Flight Radar API is alive and ready
- **get_flights**: Get a list of flights with optional filtering and limiting
- **get_flight_by_id**: Get detailed information about a specific flight
- **get_flight_positions**: Get position data for a specific flight
- **get_all_positions**: Get all position data with optional filtering
- **get_aircraft**: Get aircraft information by ICAO 24-bit address

## Installation

1. Set up environment variables:
```bash
# Create a .env file with your Flight Radar API base URL
echo "FLIGHTRADAR_API_BASE_URL=your_api_base_url_here" > .env
```

2. Install dependencies:
```bash
uv sync
```

This will:
- Create a virtual environment automatically if one doesn't exist
- Install all dependencies specified in pyproject.toml
- Set up the project for development

## Usage

### Running the Server Standalone
```bash
uv run flight_radar_mcp.py
```

### Configuring with Claude Desktop

Add the following to your Claude Desktop MCP configuration file:

```json
{
  "mcpServers": {
    "flightradar": {
      "command": "/path/to/uv",
      "args": ["run", "--directory", "/your/checkout/dir", "flight_radar_mcp.py"],
      "env": {
        "FLIGHTRADAR_API_BASE_URL": "https://radar-api.com"
      }
    }
  }
}

```

## API Endpoints Covered

- `GET /api/v1/info` - Get meta information
- `GET /api/v1/alive` - Check if API is alive
- `GET /api/v1/ready` - Check if API is ready
- `GET /api/v1/flights` - Get flights with optional filtering
- `GET /api/v1/flights/{flight_id}` - Get specific flight details
- `GET /api/v1/flights/{flight_id}/positions` - Get flight position data
- `GET /api/v1/positions` - Get all position data
- `GET /api/v1/aircraft/{icao24addr}` - Get aircraft information

## Example Usage

Once configured, you can use the MCP server in Claude to:

1. **Get current flights**: "Show me all current flights"
2. **Filter military flights**: "Get all military flights"
3. **Track specific aircraft**: "Get information for aircraft with ICAO address ABC123"
4. **Get flight positions**: "Show the position history for flight XYZ456"
5. **Check API status**: "Is the flight radar API working?"

## Data Models

### FlightDto
- `id`: Flight identifier
- `icao24`: ICAO 24-bit address
- `cls`: Flight class (optional)
- `lstCntct`: Last contact timestamp
- `firstCntct`: First contact timestamp

### AircraftDto
- `icao24`: ICAO 24-bit address
- `reg`: Registration (optional)
- `icaoType`: ICAO aircraft type (optional)
- `type`: Aircraft type (optional)
- `op`: Operator (optional)

## Error Handling

The server includes comprehensive error handling for:
- Network connectivity issues
- API rate limiting
- Invalid parameters
- Missing flight/aircraft data

## Requirements

- Python 3.10+
- uv package manager