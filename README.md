# 🌤️ Weather AI Agent

An intelligent weather forecasting agent powered by Claude 4.5 Sonnet on Amazon Bedrock. This project demonstrates agentic AI principles by combining AI reasoning with real-world API interactions to deliver weather forecasts.

## 🎯 What is Agentic AI?

This project showcases **Agentic AI** - AI systems that can:
- **🧠 Reason**: Understand user intent and plan actions
- **🔗 Act**: Execute real-world tasks (API calls)
- **📊 Process**: Transform raw data into useful insights
- **🔄 Adapt**: Handle various input formats and edge cases

## ✨ Features

- **Intelligent Location Parsing**: Handles city names, ZIP codes, state names, and descriptive queries
- **Multi-Step Reasoning**: AI plans and executes a sequence of API calls
- **Real-Time Weather Data**: Fetches live data from the National Weather Service API
- **Natural Language Summaries**: Converts complex JSON responses into readable forecasts
- **Two Interfaces**: CLI for quick queries, Web UI for interactive exploration

## 🏗️ Architecture

```
User Input → AI Planning → Points API → Forecast API → AI Processing → Results
```

1. **User Input**: Location name or description
2. **AI Planning**: Claude generates appropriate API calls
3. **Points API**: Fetch weather office coordinates
4. **Forecast API**: Get detailed weather data
5. **AI Processing**: Convert raw data to summary
6. **Display Results**: Present forecast to user

## 📋 Prerequisites

- Python 3.8+
- AWS account with Bedrock access
- AWS credentials configured
- Access to Claude 4.5 Sonnet model in Amazon Bedrock

## 🚀 Installation

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

Ensure your AWS credentials have permissions for:
- `bedrock:InvokeModel`
- Access to Claude 4.5 Sonnet model in `us-west-2` region

## 💻 Usage

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

## 🧪 Example Queries

Try these location formats:

- **City names**: `Seattle`, `New York City`, `Miami, FL`
- **ZIP codes**: `90210`, `10001`
- **Descriptive queries**: `Largest city in California`, `National park near Homestead in Florida`

## 📁 Project Structure

```
.
├── weather_agent_cli.py      # Command-line interface
├── weather_agent_web.py      # Streamlit web interface
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔧 How It Works

### 1. AI Planning Phase
Claude analyzes the location input and generates the appropriate National Weather Service API URL with coordinates.

### 2. Points API Call
Fetches weather office information for the coordinates:
```
https://api.weather.gov/points/{lat},{lon}
```

### 3. Forecast API Call
Retrieves detailed forecast data from the weather office endpoint.

### 4. AI Processing Phase
Claude converts raw JSON weather data into a natural language summary with:
- Current conditions
- Multi-day forecast
- Temperature ranges
- Precipitation chances
- Notable weather patterns

## 🛠️ Technical Details

### AWS Services Used
- **Amazon Bedrock**: AI model hosting and inference
- **Claude 4.5 Sonnet**: Language model for reasoning and processing

### External APIs
- **National Weather Service API**: Free, public weather data (no API key required)

### Key Technologies
- **boto3**: AWS SDK for Python
- **Streamlit**: Web interface framework
- **subprocess**: System command execution for API calls

## ⚠️ Important Notes

- This project uses the National Weather Service API for educational purposes
- For critical weather decisions, consult official weather sources
- API rate limits apply to the NWS API
- AWS Bedrock usage incurs costs based on token consumption

## 🔐 Security Considerations

- Never commit AWS credentials to version control
- Use IAM roles with least-privilege permissions
- Consider using AWS Secrets Manager for production deployments
- Validate and sanitize all user inputs

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Add support for international weather APIs
- Implement caching to reduce API calls
- Add weather alerts and warnings
- Support for hourly forecasts
- Add unit tests

## 📄 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

- National Weather Service for providing free weather data
- Anthropic for Claude AI capabilities
- AWS for Bedrock infrastructure

## 📞 Support

For issues or questions:
- Check the NWS API documentation: https://www.weather.gov/documentation/services-web-api
- Review AWS Bedrock documentation: https://docs.aws.amazon.com/bedrock/

---

**Built with ❤️ using Claude 4.5 Sonnet on Amazon Bedrock**
