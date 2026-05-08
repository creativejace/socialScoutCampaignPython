import json
import os
from main import lambda_handler

class LocalContext:
    
    function_name = "local_test"
    aws_request_id = "test_request_id"

if __name__ == "__main__":
        # Sample event with run_id
        test_event = { "body": "{\"campaign_id\": \"651c58a0c7cdede479ad539e\"}" }

        test = os.getenv("ENSEMBLE_TOKEN")

        # Create a local context object
        test_context = LocalContext()

        # Call the lambda_handler function with the test event and context
        response = lambda_handler(test_event, test_context)

        # Print the response
        print("Lambda Response:", response)