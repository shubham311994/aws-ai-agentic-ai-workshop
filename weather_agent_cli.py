# Import necessary libraries
import boto3        # AWS SDK for Python - allows us to interact with AWS services
import json         # For handling JSON data
import subprocess   # For running system commands like curl
import time         # For adding delays and timing operations
from datetime import datetime  # For timestamps and date operations

def call_claude_sonnet(prompt):
    """
    This function sends a prompt to Claude 4.5 Sonnet and gets a response.
    This is the "brain" of our agent - where the AI thinking happens.
    
    Args:
        prompt (str): The question or instruction we want to send to Claude
    
    Returns:
        tuple: (success: bool, response: str) - success status and Claude's response or error message
    """
    # Create a connection to Amazon Bedrock service
    # Bedrock is AWS's service for accessing AI models like Claude
    bedrock = boto3.client(
        service_name='bedrock-runtime',  # Specify we want the runtime version for making AI calls
        region_name='us-west-2'          # AWS region - using us-west-2 as specified
    )
    
    try:
        # Send our prompt to Claude and get a response
        response = bedrock.converse(
            # Specify which version of Claude we want to use
            modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',  # Claude 4.5 Sonnet
            
            # Format our message - Claude expects messages in a specific structure
            messages=[
                {
                    "role": "user",                    # We are the user asking a question
                    "content": [{"text": prompt}]      # Our actual question/prompt
                }
            ],
            
            # Configure how Claude should respond
            inferenceConfig={
                "maxTokens": 2000,    # Maximum length of response (tokens ≈ words)
                "temperature": 0.7   # Creativity level (0=very focused, 1=very creative)
            }
        )
        
        # Extract the actual text response from Claude's response structure
        # The response comes nested in a complex structure, so we dig down to get the text
        return True, response['output']['message']['content'][0]['text']
        
    except Exception as e:
        # If something goes wrong, return an error message
        return False, f"Error calling Claude: {str(e)}"

def execute_curl_command(url):
    """
    Execute a curl command to fetch data from an API.
    This is how our agent "acts" in the real world - making HTTP requests.
    
    Args:
        url (str): The URL to fetch data from
    
    Returns:
        tuple: (success: bool, response: str) - success status and API response or error message
    """
    try:
        # Use curl command to make HTTP request
        # curl is a command-line tool for making HTTP requests
        result = subprocess.run(
            ['curl', '-s', url],  # -s flag makes curl silent (no progress info)
            capture_output=True,   # Capture the output so we can process it
            text=True,            # Return output as text (not bytes)
            timeout=30            # Give up after 30 seconds
        )
        
        # Check if the command was successful
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Curl command failed: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return False, "Request timed out after 30 seconds"
    except Exception as e:
        return False, f"Error executing curl: {str(e)}"

def detect_location_region(location):
    """
    Use Claude to determine if location is in USA or Australia.
    
    Args:
        location (str): The location provided by the user
    
    Returns:
        tuple: (success: bool, region: str) - success status and region ('USA' or 'AUSTRALIA')
    """
    prompt = f"""
Determine if this location is in the United States or Australia: "{location}"

Consider:
- Australian cities: Sydney, Melbourne, Brisbane, Perth, Adelaide, Canberra, etc.
- Australian states/territories: NSW, VIC, QLD, WA, SA, TAS, NT, ACT
- Australian postcodes: 4 digits (e.g., 2000, 3000, 4000)
- US locations: US cities, states, ZIP codes (5 digits)

Return ONLY one word: USA or AUSTRALIA
"""
    
    success, response = call_claude_sonnet(prompt)
    if success:
        region = response.strip().upper()
        if region in ['USA', 'AUSTRALIA']:
            return True, region
        return False, "Could not determine region"
    return False, response

def generate_weather_api_calls(location):
    """
    Use Claude to intelligently generate weather API calls for USA or Australia.
    
    Args:
        location (str): The location provided by the user
    
    Returns:
        tuple: (success: bool, data: dict) - success status and dict with 'region' and 'url' or error
    """
    print(f"AI is analyzing '{location}'...")
    
    # Detect region
    success, region = detect_location_region(location)
    if not success:
        return False, region
    
    print(f"Detected region: {region}")
    
    if region == 'USA':
        prompt = f"""
You are an expert at working with the National Weather Service (NWS) API.

Generate the NWS API URL for "{location}".

Instructions:
1. Determine the latitude and longitude coordinates
2. Generate: https://api.weather.gov/points/{{lat}},{{lon}}

Example for Seattle: https://api.weather.gov/points/47.6062,-122.3321

Return ONLY the complete URL, nothing else.
"""
    else:  # AUSTRALIA
        prompt = f"""
You are an expert at working with Australian weather data.

Generate coordinates for "{location}" in Australia.

Instructions:
1. Determine the latitude and longitude for this Australian location
2. Return ONLY in this exact format: LAT,LON

Examples:
- Sydney: -33.8688,151.2093
- Melbourne: -37.8136,144.9631
- Brisbane: -27.4698,153.0251

Return ONLY the coordinates in format: LAT,LON
"""
    
    success, response = call_claude_sonnet(prompt)
    
    if success:
        response = response.strip()
        if region == 'USA':
            if response.startswith('https://api.weather.gov/points/'):
                return True, {'region': 'USA', 'url': response}
            return False, f"Invalid URL: {response}"
        else:  # AUSTRALIA
            try:
                lat, lon = response.split(',')
                lat, lon = float(lat.strip()), float(lon.strip())
                # BOM API uses nearest observation station
                url = f"http://www.bom.gov.au/fwo/IDN60901/IDN60901.94768.json"
                return True, {'region': 'AUSTRALIA', 'coords': (lat, lon), 'url': url}
            except:
                return False, f"Invalid coordinates: {response}"
    
    return False, response

def get_forecast_url_from_points_response(points_json):
    """
    Extract the forecast URL from the NWS Points API response.
    
    Args:
        points_json (str): JSON response from the Points API
    
    Returns:
        tuple: (success: bool, forecast_url: str) - success status and forecast URL or error message
    """
    try:
        data = json.loads(points_json)
        forecast_url = data['properties']['forecast']
        return True, forecast_url
    except (json.JSONDecodeError, KeyError) as e:
        return False, f"Error parsing Points API response: {str(e)}"

def process_weather_response(raw_json, location, region='USA'):
    """
    Use Claude to convert raw weather API JSON into a human-readable summary.
    
    Args:
        raw_json (str): Raw JSON response from weather API
        location (str): Original location for context
        region (str): 'USA' or 'AUSTRALIA'
    
    Returns:
        tuple: (success: bool, summary: str) - success status and processed summary or error message
    """
    api_source = "National Weather Service" if region == 'USA' else "Bureau of Meteorology"
    
    prompt = f"""
You are a weather information specialist. I have raw {api_source} forecast data for "{location}" that needs to be converted into a clear, helpful summary for a general audience.

Raw API Response:
{raw_json}

Please create a weather summary that includes:
1. A brief introduction with the location
2. Current conditions and today's forecast
3. The next 2-3 days outlook with key details (temperature, precipitation, wind)
4. Any notable weather patterns or alerts
5. Format the response to be easy to read and understand

Make it informative and practical for someone planning their activities. Focus on being helpful and clear.
"""
    
    print(f"AI is processing weather data and creating summary...")
    success, response = call_claude_sonnet(prompt)
    
    return success, response

def run_weather_agent():
    """
    Main function that orchestrates our AI agent.
    This demonstrates the complete agentic workflow.
    """
    print("Welcome to the Weather AI Agent!")
    print("This agent uses Claude 4.5 Sonnet to help you get weather forecasts.")
    print("Supports locations in USA and Australia!")
    print("=" * 60)
    
    while True:
        # Get user input
        location = input("\n Enter a location name or description (or 'quit' to exit): ").strip()
        
        if location.lower() in ['quit', 'exit', 'q']:
            print("Thanks for using the Weather Agent!")
            break
            
        if not location:
            print("Please enter a location name or description.")
            continue
            
        print(f"\n Starting weather analysis for '{location}'...")
        print("-" * 40)
        
        # Step 1: AI generates the API URL and detects region
        print("Step 1: AI Planning Phase")
        success, api_data = generate_weather_api_calls(location)
        
        if not success:
            print(f" Failed to generate API calls: {api_data}")
            continue
        
        region = api_data['region']
        print(f" Region: {region}")
        
        if region == 'USA':
            points_url = api_data['url']
            print(f" Generated Points API URL: {points_url}")
            
            # Step 2: Execute the Points API call
            print("\n Step 2: Points API Execution")
            print("Fetching location data from National Weather Service...")
            success, points_response = execute_curl_command(points_url)
            
            if not success:
                print(f" Failed to fetch points data: {points_response}")
                continue
                
            print(f" Received points data")
            
            # Step 3: Extract forecast URL from Points response
            print("\n Step 3: Extracting Forecast URL")
            success, forecast_url = get_forecast_url_from_points_response(points_response)
            
            if not success:
                print(f" Failed to extract forecast URL: {forecast_url}")
                continue
                
            print(f" Forecast URL: {forecast_url[:60]}...")
            
            # Step 4: Execute the Forecast API call
            print("\n Step 4: Forecast API Execution")
            print("Fetching weather forecast data...")
            success, forecast_response = execute_curl_command(forecast_url)
            
            if not success:
                print(f" Failed to fetch forecast data: {forecast_response}")
                continue
                
            print(f" Received {len(forecast_response)} characters of forecast data")
            
        else:  # AUSTRALIA
            # For Australia, use Open-Meteo API (free, no key required)
            lat, lon = api_data['coords']
            forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode,windspeed_10m&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
            
            print(f" Generated forecast URL for coordinates: {lat},{lon}")
            
            # Step 2: Execute the Forecast API call
            print("\n Step 2: Forecast API Execution")
            print("Fetching weather forecast data from Open-Meteo...")
            success, forecast_response = execute_curl_command(forecast_url)
            
            if not success:
                print(f" Failed to fetch forecast data: {forecast_response}")
                continue
                
            print(f" Received {len(forecast_response)} characters of forecast data")
        
        # Step 5: AI processes the response
        step_num = 5 if region == 'USA' else 3
        print(f"\nStep {step_num}: AI Analysis Phase")
        success, summary = process_weather_response(forecast_response, location, region)
        
        if not success:
            print(f" Failed to process data: {summary}")
            continue
            
        # Step 6: Display results
        step_num = 6 if region == 'USA' else 4
        print(f"\nStep {step_num}: Weather Forecast")
        print("=" * 60)
        print(summary)
        print("=" * 60)
        
        print(f"\n Weather analysis complete for '{location}'!")

# Run the agent when the script is executed
if __name__ == "__main__":
    run_weather_agent()