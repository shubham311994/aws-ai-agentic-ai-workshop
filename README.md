# 🌤️ Weather AI Agent

A weather agent that uses Claude on Amazon Bedrock to fetch and explain weather forecasts. Works with locations in the USA and Australia.

## What This Does

Give it a location, and it'll:
1. Figure out if you're asking about a US or Australian location
2. Call the right weather API
3. Turn the raw data into something actually readable

The interesting part is watching Claude plan and execute the API calls on its own - that's the "agentic" bit.

## Features

- Handles city names, ZIP codes, postcodes, whatever
- Works with USA (National Weather Service) and Australia (Open-Meteo)
- Two ways to use it: command line or web interface
- Shows you each step as it happens

## Prerequisites

- Python 3.8+
- AWS account with Bedrock access
- AWS credentials configured
- Access to Claude 4.5 Sonnet model in Amazon Bedrock

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials:
```bash
aws configure
```

Make sure your credentials have `bedrock:InvokeModel` permissions and access to Claude 4.5 Sonnet in `us-west-2`.

## Usage

### CLI Version

Run the command-line interface:

```bash
python weather_agent_cli.py
```

Example interaction:
```
Enter a location name or description: Seattle
```

### Web Interface

Launch the Streamlit web application:

```bash
streamlit run weather_agent_web.py
```

Then open your browser to `http://localhost:8501`

## Example Queries

**USA:**
- City names: `Seattle`, `New York City`, `Miami, FL`
- ZIP codes: `90210`, `10001`
- Descriptive: `Largest city in California`

**Australia:**
- City names: `Sydney`, `Melbourne`, `Brisbane`, `Perth`
- States: `NSW`, `Victoria`, `Queensland`
- Postcodes: `2000`, `3000`, `4000`

## How It Works

**For USA locations:**
1. Claude detects it's a US location
2. Generates coordinates and calls NWS Points API
3. Extracts forecast URL from response
4. Fetches detailed forecast data
5. Claude converts JSON to readable summary

**For Australian locations:**
1. Claude detects it's an Australian location
2. Generates coordinates for the location
3. Calls Open-Meteo API with coordinates
4. Claude converts JSON to readable summary

## Technical Stack

- **Amazon Bedrock** - Hosts Claude 4.5 Sonnet
- **National Weather Service API** - Free US weather data
- **Open-Meteo API** - Free Australian weather data
- **Streamlit** - Web interface
- **boto3** - AWS SDK for Python

## Important Notes

- This uses public weather APIs for educational purposes
- For critical weather decisions, use official sources
- AWS Bedrock usage incurs costs based on token consumption
- Never commit AWS credentials to version control

## Contributing

Ideas for improvements:
- Add caching to reduce API calls
- Support for weather alerts
- Hourly forecasts
- More countries

## Acknowledgments

- National Weather Service for free US weather data
- Open-Meteo for free Australian weather data
- Anthropic for Claude
- AWS for Bedrock

---

**Built with Claude 4.5 Sonnet on Amazon Bedrock**
