import requests
import json
from config import model

def resume_generator(inputData: str):
    try:
        response = model.generate_content(inputData)
        try:
            json_data = json.loads(response.text)  
        except json.JSONDecodeError:
            json_data = {"error": "Response is not valid JSON", "message": result}

        # Return the parsed JSON data
        return json_data    
    except requests.exceptions.RequestException as error:
        print(f"Error during API request: {error}")
        return {"error": "Failed to interact with Gemini AI"}