import unittest
import json
from unittest.mock import patch, MagicMock
import base64
import os

# Add the parent directory to the Python path to allow importing the `app`
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

class FlaskAppTests(unittest.TestCase):

    def setUp(self):
        """Set up a test client for the Flask application."""
        self.app = app.test_client()
        self.app.testing = True

    @patch('main.vertexai')
    @patch('main.GenerativeModel')
    def test_hello_success(self, mock_generative_model, mock_vertexai):
        """Test the main endpoint with a valid request."""
        # Mock the Vertex AI and GenerativeModel initialization
        mock_vertexai.init.return_value = None
        
        # Mock the model's response
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Mocked AI response"
        mock_model_instance.generate_content.return_value = mock_response
        mock_generative_model.return_value = mock_model_instance

        # Prepare the request data
        file_content = "This is a test error log."
        file_base64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
        data = {
            "file_base64": file_base64,
            "mood": "helpful"
        }

        # Send the POST request
        response = self.app.post('/',
                                 data=json.dumps(data),
                                 content_type='application/json')

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), "Mocked AI response")
        
        # Verify that Vertex AI was initialized and the model was called
        mock_vertexai.init.assert_called_once()
        mock_generative_model.assert_called_once_with("gemini-2.0-flash-001")
        mock_model_instance.generate_content.assert_called_once()

    def test_missing_file_base64(self):
        """Test the endpoint when 'file_base64' is missing from the request."""
        data = {"mood": "neutral"}
        response = self.app.post('/',
                                 data=json.dumps(data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertEqual(response_json['error'], "Missing 'file_base64' in request body")

    def test_invalid_base64(self):
        """Test the endpoint with a corrupted base64 string."""
        data = {
            "file_base64": "this-is-not-base64",
            "mood": "analytical"
        }
        response = self.app.post('/',
                                 data=json.dumps(data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.data.decode('utf-8'))
        self.assertIn("Failed to decode base64", response_json['error'])

if __name__ == '__main__':
    unittest.main()
