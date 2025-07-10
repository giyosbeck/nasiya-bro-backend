#!/usr/bin/env python3
"""
Cron job script to automatically check for expired user subscriptions.
This script can be run via cron to automatically deactivate expired users.

Usage:
    python3 cron_subscription_check.py

Add to crontab to run daily at 2 AM:
    0 2 * * * /path/to/python3 /path/to/cron_subscription_check.py
"""
import sys
import os
import requests
from datetime import datetime

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.subscription_service import check_and_deactivate_expired_users

def main():
    """Main function to run the subscription check."""
    print(f"Starting subscription check at {datetime.now()}")
    
    try:
        # Option 1: Direct function call (recommended for local cron jobs)
        result = check_and_deactivate_expired_users()
        
        print(f"Subscription check completed: {result['message']}")
        print(f"Total deactivated users: {result['total_deactivated']}")
        
        if result['deactivated_users']:
            print("Deactivated users:")
            for user in result['deactivated_users']:
                print(f"  - {user['name']} ({user['phone']}) - Expired: {user['subscription_end_date']}")
        
        # Log result to file
        with open('subscription_check.log', 'a') as log_file:
            log_file.write(f"{datetime.now()}: {result['message']}\n")
        
        return 0 if result['success'] else 1
        
    except Exception as e:
        error_msg = f"Error during subscription check: {str(e)}"
        print(error_msg)
        
        # Log error to file
        with open('subscription_check.log', 'a') as log_file:
            log_file.write(f"{datetime.now()}: ERROR - {error_msg}\n")
        
        return 1

def check_via_api():
    """
    Alternative method: Check via API endpoint.
    Use this if you want to call the API endpoint instead of direct function call.
    """
    try:
        # Replace with your actual API URL
        api_url = "http://localhost:8000/api/v1/users/auto-check-expired"
        
        response = requests.post(api_url)
        response.raise_for_status()
        
        result = response.json()
        print(f"API check completed: {result['message']}")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return None

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)