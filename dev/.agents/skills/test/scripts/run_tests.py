#!/usr/bin/env python3
import sys
import os
import urllib.request
import json
from datetime import datetime

# Environments
ENV_CONFIGS = {
    "dev": {
        "web_url": "https://maliyil-clinic.github.io/dev/index.html",
        "contact_url": "https://maliyil-clinic.github.io/dev/contact.html",
        "script_url": "https://script.google.com/macros/s/AKfycbz_8PsBZ4qFAZE_f8cM8-s4jaybIe0Dv-fP29QgFlVZVTuGvbfCbk1pWtmrIN6LNSEv/exec"
    },
    "prod": {
        "web_url": "https://maliyil-clinic.github.io/index.html",
        "contact_url": "https://maliyil-clinic.github.io/contact.html",
        "script_url": "https://script.google.com/macros/s/AKfycbxTXMqMBtB0ciMwHfiOceKQQYG_JHQGaiROuXLaY1gmXRvKQWIiF4f_558y7ItCs9UIEA/exec"
    }
}

def test_frontend_load(config):
    """Test 1: Verify that the hosted website returns HTTP 200."""
    print("🌐 Testing Website Frontend Load...")
    url = config["web_url"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Maliyil-Test-Suite"})
        with urllib.request.urlopen(req, timeout=10) as response:
            code = response.getcode()
            if code == 200:
                print(f"✅ Success: Website loaded successfully. URL: {url} (HTTP 200)")
                return True
            else:
                print(f"❌ Failure: Website returned HTTP status code {code} for URL: {url}")
                return False
    except Exception as e:
        print(f"❌ Failure: Could not load website at {url}. Error: {e}")
        return False

def test_apps_script_connection(config):
    """Test 2: Verify that the Google Apps Script Web App responds correctly with JSON data."""
    print("\n🔗 Testing Google Apps Script Database Connection...")
    
    # Query getSlots for a placeholder date in the future
    date_str = "2026-07-20"
    url = f"{config['script_url']}?action=getSlots&date={date_str}"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Maliyil-Test-Suite"})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode()
            data = json.loads(content)
            
            # Apps Script JSON validation
            if data.get("status") == "success":
                print(f"✅ Success: Google Apps Script responded successfully.")
                print(f"   API Response: {content[:100]}...")
                return True
            else:
                print(f"❌ Failure: Apps Script API returned error response: {content}")
                return False
    except Exception as e:
        print(f"❌ Failure: Could not connect to Apps Script Web App. Error: {e}")
        return False

def test_local_file_integrity():
    """Test 3: Verify local HTML structure has expected configuration variables and content."""
    print("\n📂 Checking Local File Integrity...")
    success = True
    
    # 1. Verify index.html has Holter Monitoring (HM)
    index_path = "index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "Holter Monitoring (HM)" in content:
                print("✅ Success: index.html contains updated text 'Holter Monitoring (HM)'.")
            else:
                print("❌ Failure: index.html does not contain the updated 'Holter Monitoring (HM)' header.")
                success = False
    else:
        print(f"❌ Failure: Local {index_path} file not found.")
        success = False
        
    # 2. Verify contact.html has the expected Apps Script URL configs
    contact_path = "contact.html"
    if os.path.exists(contact_path):
        with open(contact_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "DEV_SCRIPT_URL" in content and "PROD_SCRIPT_URL" in content:
                print("✅ Success: contact.html contains DEV_SCRIPT_URL and PROD_SCRIPT_URL.")
            else:
                print("❌ Failure: contact.html configuration variables are missing or incorrect.")
                success = False
    else:
        print(f"❌ Failure: Local {contact_path} file not found.")
        success = False
        
    return success

def main():
    if len(sys.argv) < 2:
        env = "dev"
    else:
        env = sys.argv[1].lower()
        
    if env not in ENV_CONFIGS:
        print(f"Error: Unknown environment '{env}'. Choose 'dev' or 'prod'.")
        sys.exit(1)
        
    print(f"==================================================")
    print(f"📋 Running Automated Tests for Environment: {env.upper()}")
    print(f"==================================================")
    
    frontend_ok = test_frontend_load(ENV_CONFIGS[env])
    api_ok = test_apps_script_connection(ENV_CONFIGS[env])
    local_ok = test_local_file_integrity()
    
    print(f"\n==================================================")
    print(f"📊 Test Suite Summary for {env.upper()}:")
    print(f"   - Frontend Availability: {'PASS' if frontend_ok else 'FAIL'}")
    print(f"   - Database API Connection: {'PASS' if api_ok else 'FAIL'}")
    print(f"   - Local Code Integrity: {'PASS' if local_ok else 'FAIL'}")
    print(f"==================================================")
    
    if frontend_ok and api_ok and local_ok:
        print("\n💚 ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)
    else:
        print("\n❤️ SOME TESTS FAILED. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
