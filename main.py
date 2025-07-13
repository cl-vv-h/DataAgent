from dotenv import load_dotenv
load_dotenv(override=True)

from utils.output_logger import OutputLogger
import sys

# Initialize output logging
sys.stdout = OutputLogger()


from backend import flask_app
if __name__ == '__main__':
    print("Starting Flask server for stock analysis...")
    print("API endpoints:")
    print("  POST /analyze - Analyze stock with 6-digit ticker")
    print("  GET /health - Health check")
    print("  GET / - API information")
    print("\nExample usage:")
    print('  curl -X POST http://localhost:5000/analyze -H "Content-Type: application/json" -d \'{"ticker": "000001"}\'')
    
    flask_app.run(host='0.0.0.0', port=5000, debug=True)





