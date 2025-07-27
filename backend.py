from langchain_core.messages import HumanMessage

from workflow import app
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import datetime

# Create Flask app
flask_app = Flask(__name__)
CORS(flask_app)  # Enable CORS for all routes

@flask_app.route('/analyze', methods=['POST'])
def analyze_stock():
    """
    Analyze a stock using the 6-digit ticker symbol
    Expected JSON payload: {"ticker": "000001"}
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or 'ticker' not in data:
            return jsonify({
                'error': 'Missing ticker parameter',
                'message': 'Please provide a ticker in the request body: {"ticker": "000001"}'
            }), 400
        
        ticker = data['ticker']
        
        # Validate ticker format (6 digits)
        if not re.match(r'^\d{6}$', ticker):
            return jsonify({
                'error': 'Invalid ticker format',
                'message': 'Ticker must be exactly 6 digits (e.g., "000001")'
            }), 400
        
        # Prepare initial state for the workflow
        initial_state = {
            "messages": [
                HumanMessage(content=f"Please analyze stock with ticker {ticker}")
            ],
            "data": {
                "ticker": ticker,
                "start_date": None,  # Will be calculated in market_data_agent
                "end_date": None,    # Will be calculated in market_data_agent
            },
            "metadata": {
                "show_reasoning": True
            }
        }
        
        # Run the workflow
        print(f"Starting analysis for ticker: {ticker}")
        result = app.invoke(initial_state)
        
        # Extract the final result from the workflow
        final_data = result.get("data", {})
        final_messages = result.get("messages", [])
        
        # Prepare response
        response_data = {
            "ticker": ticker,
            "status": "completed",
            "analysis": {
                "market_data": final_data.get("market_data", {}),
                "financial_metrics": final_data.get("financial_metrics", {}),
                "financial_line_items": final_data.get("financial_line_items", {}),
                "prices": final_data.get("prices", []),
                "start_date": final_data.get("start_date"),
                "end_date": final_data.get("end_date"),
            },
            "messages": [msg.content for msg in final_messages if hasattr(msg, 'content')]
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500
    
@flask_app.route('/analyze', methods=['GET'])
def get_analyze_stock():
    """
    Analyze a stock using the 6-digit ticker symbol passed as a URL parameter,
    e.g. /analyze?ticker=000001
    """
    try:
        market = request.args.get('ticker', None)
        ticker = request.args.get('ticker', None)
        start_date = None
        end_date = datetime.now().strftime("%Y%m%d")
        if not ticker:
            return jsonify({
                'error': 'Missing ticker parameter',
                'message': 'Please provide a ticker as a URL parameter, e.g. /analyze?ticker=000001'
            }), 400
        
        if not re.match(r'^\d{6}$', ticker):
            return jsonify({
                'error': 'Invalid ticker format',
                'message': 'Ticker must be exactly 6 digits (e.g., "000001")'
            }), 400
        
        # Prepare initial state for the workflow
        initial_state = {
            "messages": [
                HumanMessage(content=f"请为以下股票提供详细分析，该股票代码为： {market + ticker}")
            ],
            "data": {
                "market": market,
                "ticker": ticker,
                "start_date": start_date,  # Will be set later
                "end_date": end_date,    # Will be set later
            },
            "metadata": {
                "show_reasoning": True
            }
        }
        
        print(f"Starting analysis for ticker: {ticker}")
        result = app.invoke(initial_state)
        
        final_data = result.get("data", {})
        final_messages = result.get("messages", [])
        
        response_data = {
            "ticker": ticker,
            "status": "completed",
            "analysis": {
                "market_data": final_data.get("market_data", {}),
                "financial_metrics": final_data.get("financial_metrics", {}),
                "financial_line_items": final_data.get("financial_line_items", {}),
                "prices": final_data.get("prices", []),
                "start_date": final_data.get("start_date"),
                "end_date": final_data.get("end_date"),
            },
            "messages": [msg.content for msg in final_messages if hasattr(msg, 'content')]
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return jsonify({
            'error': 'Analysis failed',
            'message': str(e)
        }), 500

@flask_app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Stock analysis API is running'
    }), 200

@flask_app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Stock Analysis API',
        'endpoints': {
            'POST /analyze': 'Analyze a stock using 6-digit ticker',
            'GET /health': 'Health check',
            'GET /': 'This information'
        },
        'usage': {
            'analyze': 'Send POST request to /analyze with {"ticker": "000001"}'
        }
    }), 200

@flask_app.route('/qwe', methods=['GET'])
def qwe():
    """Root endpoint with API information"""
    run_hedge_fund("600310")
    return jsonify({
        'message': 'Stock Analysis API',
        'endpoints': {
            'POST /analyze': 'Analyze a stock using 6-digit ticker',
            'GET /health': 'Health check',
            'GET /': 'This information'
        },
        'usage': {
            'analyze': 'Send POST request to /analyze with {"ticker": "000001"}'
        }
    }), 200

def run_hedge_fund(ticker: str, start_date: str="2024-03-10", end_date: str="2025-03-10", num_of_news: int = 10):
    final_state = app.invoke(
        {
            "messages": [
                HumanMessage(
                    content="Make a trading decision based on the provided data.",
                )
            ],
            "data": {
                "ticker": ticker,
                "start_date": start_date,
                "end_date": end_date,
                "num_of_news": num_of_news,
            },
            "metadata": {
                "show_reasoning": False
            }
        },
    )
    return final_state["messages"][-1].content
