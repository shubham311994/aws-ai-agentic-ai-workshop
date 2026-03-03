import streamlit as st
import boto3
import subprocess
import json
import time
from datetime import datetime
from PIL import Image
import os

# Page configuration
st.set_page_config(
    page_title="Weather AI Agent",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .step-container {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .step-header {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .success-box {
        border-left: 5px solid #28a745;
        background-color: #d4edda;
        padding: 10px;
        margin: 10px 0;
        color: #000000;
    }
    .error-box {
        border-left: 5px solid #dc3545;
        background-color: #f8d7da;
        padding: 10px;
        margin: 10px 0;
        color: #000000;
    }
    .info-box {
        border-left: 5px solid #17a2b8;
        background-color: #d1ecf1;
        padding: 10px;
        margin: 10px 0;
        color: #000000;
    }
</style>
""", unsafe_allow_html=True)

def call_claude_sonnet(prompt):
    """
    Connect to Claude 4.5 Sonnet via Amazon Bedrock
    """
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2'
    )
    
    try:
        response = bedrock.converse(
            modelId='us.anthropic.claude-sonnet-4-5-20250929-v1:0',
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ],
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.7
            }
        )
        
        return True, response['output']['message']['content'][0]['text']
        
    except Exception as e:
        return False, f"Error calling Claude: {str(e)}"

def execute_curl_command(url):
    """
    Execute curl command to fetch API data
    """
    try:
        result = subprocess.run(
            ['curl', '-s', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
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
    Use Claude to generate weather API calls for USA or Australia.
    """
    success, region = detect_location_region(location)
    if not success:
        return False, region
    
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
                return True, {'region': 'AUSTRALIA', 'coords': (lat, lon)}
            except:
                return False, f"Invalid coordinates: {response}"
    
    return False, response

def get_forecast_url_from_points_response(points_json):
    """
    Extract forecast URL from Points API response
    """
    try:
        data = json.loads(points_json)
        forecast_url = data['properties']['forecast']
        return True, forecast_url
    except (json.JSONDecodeError, KeyError) as e:
        return False, f"Error parsing Points API response: {str(e)}"

def process_weather_response(raw_json, location, region='USA'):
    """
    Use Claude to process weather API response
    """
    api_source = "National Weather Service" if region == 'USA' else "Open-Meteo"
    
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
    
    success, response = call_claude_sonnet(prompt)
    return success, response

# Sidebar with information
st.sidebar.title("🤖 About This Agent")
st.sidebar.markdown("""
This AI agent demonstrates **Agentic AI** principles:

**🧠 Intelligence**: Uses Claude 4.5 Sonnet to understand locations and plan API calls

**🔗 Action**: Automatically calls weather APIs (NWS for USA, Open-Meteo for Australia)

**📊 Processing**: Converts complex weather data into readable forecasts

**💬 Response**: Provides helpful, practical weather information
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏗️ Architecture")
st.sidebar.markdown("""
1. **User Input** → Location name
2. **AI Planning** → Generate API calls
3. **Points API** → Get forecast office  
4. **Forecast API** → Get weather data
5. **AI Processing** → Create summary
6. **Display Results** → Show to user
""")

# Main application
st.title("🌤️ Weather AI Agent")
st.markdown("### Powered by Claude 4.5 Sonnet on Amazon Bedrock")

st.markdown("""
This intelligent agent helps you get weather forecasts for USA and Australia locations. 
Enter any location below and watch the AI agent work through its reasoning process!
""")

# Initialize session state for results
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Input section
st.markdown("---")
location = st.text_input(
    "🔍 Enter a location name or description:",
    placeholder="e.g., Seattle, Sydney, 90210, Melbourne, New York City",
    help="You can enter city names, ZIP codes, state names, or location descriptions (USA & Australia)"
)

# Create columns for the buttons
button_col1, button_col2 = st.columns([2, 1])

with button_col1:
    get_forecast = st.button("🚀 Get Weather Forecast", type="primary")

with button_col2:
    clear_results = st.button("🗑️ Clear Results", type="secondary")

# Clear results functionality
if clear_results:
    st.session_state.show_results = False
    st.success("🗑️ Results cleared! Enter a new location to get a fresh forecast.")

if get_forecast:
    st.session_state.show_results = True

if st.session_state.show_results and get_forecast:
    if not location:
        st.error("❌ Please enter a location name or description.")
    else:
        # Create columns for better layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"## Weather Analysis for: **{location}**")
            
            # Step 1: AI Planning
            with st.container():
                st.markdown('<div class="step-container">', unsafe_allow_html=True)
                st.markdown('<div class="step-header">🧠 Step 1: AI Planning Phase</div>', unsafe_allow_html=True)
                
                with st.spinner("Claude is analyzing the location and planning the API calls..."):
                    success, api_data = generate_weather_api_calls(location)
                
                if success:
                    region = api_data['region']
                    st.markdown(f'<div class="success-box">✅ Detected region: {region}</div>', unsafe_allow_html=True)
                    
                    if region == 'USA':
                        points_url = api_data['url']
                        st.code(points_url, language="text")
                    else:
                        lat, lon = api_data['coords']
                        st.markdown(f"**Coordinates:** {lat}, {lon}")
                else:
                    st.markdown(f'<div class="error-box">❌ Failed to generate API calls: {api_data}</div>', unsafe_allow_html=True)
                    st.stop()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            if region == 'USA':
                # Step 2: Points API Execution
                with st.container():
                    st.markdown('<div class="step-container">', unsafe_allow_html=True)
                    st.markdown('<div class="step-header">🔗 Step 2: Points API Execution</div>', unsafe_allow_html=True)
                    
                    with st.spinner("Fetching location data from National Weather Service..."):
                        success, points_response = execute_curl_command(points_url)
                    
                    if success:
                        st.markdown('<div class="success-box">✅ Received location data from NWS</div>', unsafe_allow_html=True)
                        
                        with st.expander("🔍 View Raw Points API Response (first 500 characters)"):
                            st.code(points_response[:500] + "..." if len(points_response) > 500 else points_response, language="json")
                    else:
                        st.markdown(f'<div class="error-box">❌ Failed to fetch points data: {points_response}</div>', unsafe_allow_html=True)
                        st.stop()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Step 3: Extract Forecast URL
                with st.container():
                    st.markdown('<div class="step-container">', unsafe_allow_html=True)
                    st.markdown('<div class="step-header">📍 Step 3: Extracting Forecast URL</div>', unsafe_allow_html=True)
                    
                    success, forecast_url = get_forecast_url_from_points_response(points_response)
                    
                    if success:
                        st.markdown('<div class="success-box">✅ Forecast URL extracted successfully!</div>', unsafe_allow_html=True)
                        st.code(forecast_url, language="text")
                    else:
                        st.markdown(f'<div class="error-box">❌ Failed to extract forecast URL: {forecast_url}</div>', unsafe_allow_html=True)
                        st.stop()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Step 4: Forecast API Execution
                with st.container():
                    st.markdown('<div class="step-container">', unsafe_allow_html=True)
                    st.markdown('<div class="step-header">🌦️ Step 4: Forecast API Execution</div>', unsafe_allow_html=True)
                    
                    with st.spinner("Fetching weather forecast data..."):
                        success, forecast_response = execute_curl_command(forecast_url)
                    
                    if success:
                        st.markdown(f'<div class="success-box">✅ Received {len(forecast_response):,} characters of forecast data</div>', unsafe_allow_html=True)
                        
                        with st.expander("🔍 View Raw Forecast API Response (first 500 characters)"):
                            st.code(forecast_response[:500] + "..." if len(forecast_response) > 500 else forecast_response, language="json")
                    else:
                        st.markdown(f'<div class="error-box">❌ Failed to fetch forecast data: {forecast_response}</div>', unsafe_allow_html=True)
                        st.stop()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                step_num = 5
            else:  # AUSTRALIA
                # Step 2: Forecast API Execution
                lat, lon = api_data['coords']
                forecast_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weathercode,windspeed_10m&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
                
                with st.container():
                    st.markdown('<div class="step-container">', unsafe_allow_html=True)
                    st.markdown('<div class="step-header">🌦️ Step 2: Forecast API Execution</div>', unsafe_allow_html=True)
                    
                    with st.spinner("Fetching weather forecast data from Open-Meteo..."):
                        success, forecast_response = execute_curl_command(forecast_url)
                    
                    if success:
                        st.markdown(f'<div class="success-box">✅ Received {len(forecast_response):,} characters of forecast data</div>', unsafe_allow_html=True)
                        
                        with st.expander("🔍 View Raw Forecast API Response (first 500 characters)"):
                            st.code(forecast_response[:500] + "..." if len(forecast_response) > 500 else forecast_response, language="json")
                    else:
                        st.markdown(f'<div class="error-box">❌ Failed to fetch forecast data: {forecast_response}</div>', unsafe_allow_html=True)
                        st.stop()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                step_num = 3
            
            # AI Processing
            with st.container():
                st.markdown('<div class="step-container">', unsafe_allow_html=True)
                st.markdown(f'<div class="step-header">📊 Step {step_num}: AI Analysis Phase</div>', unsafe_allow_html=True)
                
                with st.spinner("Claude is processing the weather data and creating a summary..."):
                    success, summary = process_weather_response(forecast_response, location, region)
                
                if success:
                    st.markdown('<div class="success-box">✅ Weather analysis complete!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Failed to process data: {summary}</div>', unsafe_allow_html=True)
                    st.stop()
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Results
            st.markdown("---")
            st.markdown("## 🌤️ Weather Forecast")
            st.markdown(summary)
            
        with col2:
            # Real-time status updates
            st.markdown("### 📊 Process Status")
            
            status_container = st.container()
            with status_container:
                st.markdown("""
                <div class="info-box">
                <strong>🔄 Agent Workflow:</strong><br>
                ✅ Planning Phase<br>
                ✅ Points API Call<br>
                ✅ URL Extraction<br>
                ✅ Forecast API Call<br>
                ✅ Data Processing<br>
                ✅ Results Generated
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 🎯 What Makes This Agentic?")
            st.markdown("""
            - **🧠 Reasoning**: AI understands location formats
            - **📋 Planning**: Generates appropriate API call sequences
            - **🔧 Action**: Executes real-world API requests
            - **📊 Processing**: Converts raw data to insights
            - **🔄 Adaptation**: Handles different location types
            """)

# Footer
st.markdown("---")
st.markdown("""
### 🔬 About This Demo

This application demonstrates **Agentic AI** principles using:
- **Amazon Bedrock** with Claude 4.5 Sonnet for intelligent reasoning
- **National Weather Service API** for real-time weather data
- **Streamlit** for interactive web interface

**⚠️ Important**: This uses official NWS data for educational purposes. For critical weather decisions, consult official sources.
""")

# Add some example queries
st.markdown("""
### 💡 Try These Examples:

**USA Locations:**
- **Seattle** - Major city
- **90210** - ZIP code
- **New York City** - Multi-word city
- **Miami, FL** - City with state

**Australian Locations:**
- **Sydney** - Major city
- **Melbourne** - Victoria's capital
- **Brisbane** - Queensland's capital
- **Perth** - Western Australia

Simply copy any of these into the location input above and click "Get Weather Forecast"!
""")