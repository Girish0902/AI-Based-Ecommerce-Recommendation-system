#!/usr/bin/env python
"""
Reflex Deployment Validation Script
Pre-deployment checks for 'reflex deploy' to ensure backend, frontend, and env vars are properly configured.
Run this BEFORE running 'reflex deploy'
"""

import os
import sys
from pathlib import Path
import json

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_status(section, passed, message=""):
    """Print status check result."""
    if passed:
        print(f"{Colors.GREEN}✓{Colors.RESET} {section}: {message}")
    else:
        print(f"{Colors.RED}✗{Colors.RESET} {section}: {message}")
    return passed

def check_backend_files():
    """Check if all backend files exist and are included."""
    print(f"\n{Colors.BLUE}=== BACKEND FILES ==={Colors.RESET}")
    backend_files = [
        'backend/__init__.py',
        'backend/recommender.py',
        'backend/collaborative_filtering.py',
        'backend/content_filtering.py',
        'backend/rating_based.py',
        'backend/cleaning_data.py',
    ]
    
    all_exist = True
    for file in backend_files:
        exists = os.path.exists(file)
        print_status(file, exists, "Found" if exists else "MISSING")
        all_exist = all_exist and exists
    
    return all_exist

def check_frontend_files():
    """Check if all frontend files exist."""
    print(f"\n{Colors.BLUE}=== FRONTEND FILES ==={Colors.RESET}")
    frontend_dirs = ['pages', 'components', 'state']
    
    all_exist = True
    for dir_name in frontend_dirs:
        exists = os.path.isdir(dir_name)
        print_status(dir_name, exists, "Found" if exists else "MISSING")
        all_exist = all_exist and exists
    
    return all_exist

def check_data_files():
    """Check if data files exist."""
    print(f"\n{Colors.BLUE}=== DATA FILES ==={Colors.RESET}")
    data_files = ['cleaned_data.csv', 'clean_data.csv']
    
    found = False
    for file in data_files:
        exists = os.path.exists(file)
        if exists:
            size_mb = os.path.getsize(file) / (1024 * 1024)
            print_status(file, True, f"Found ({size_mb:.2f} MB)")
            found = True
        else:
            print_status(file, False, "Not found")
    
    if not found:
        print(f"{Colors.YELLOW}⚠{Colors.RESET} WARNING: No CSV data files found. Recommendations will fail!")
        return False
    return True

def check_config_files():
    """Check if configuration files exist."""
    print(f"\n{Colors.BLUE}=== CONFIG FILES ==={Colors.RESET}")
    config_files = {
        'rxconfig.py': 'Reflex configuration',
        'config.py': 'App configuration',
        'requirements.txt': 'Python dependencies',
    }
    
    all_exist = True
    for file, desc in config_files.items():
        exists = os.path.exists(file)
        print_status(file, exists, desc if exists else f"{desc} - MISSING")
        all_exist = all_exist and exists
    
    return all_exist

def check_env_configuration():
    """Check if environment variables are properly configured."""
    print(f"\n{Colors.BLUE}=== ENVIRONMENT VARIABLES ==={Colors.RESET}")
    
    # Check for .env file (should not be committed, but might exist locally)
    env_exists = os.path.exists('.env')
    print_status('.env file', env_exists, "Exists (local only)" if env_exists else "Not found (expected for deployment)")
    
    # Check for .env.example (should exist for reference)
    env_example_exists = os.path.exists('.env.example')
    print_status('.env.example', env_example_exists, "Found - reference for required variables" if env_example_exists else "MISSING - should exist")
    
    # Check if required variables are in .env or .env.example
    required_vars = [
        'FIREBASE_API_KEY',
        'FIREBASE_PROJECT_ID',
        'FIREBASE_AUTH_DOMAIN',
        'GROQ_API_KEY',
    ]
    
    optional_vars = [
        'RAZORPAY_KEY_ID',
        'RAZORPAY_KEY_SECRET',
    ]
    
    print("\n  Required variables (must be set during deployment):")
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print_status(f"  {var}", True, "Set in environment")
        else:
            print_status(f"  {var}", False, "NOT set - must configure in Reflex platform")
    
    print("\n  Optional variables:")
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print_status(f"  {var}", True, "Set in environment")
        else:
            print_status(f"  {var}", False, "Not set")
    
    return env_example_exists

def check_rxconfig():
    """Check if rxconfig.py has proper configuration for deployment."""
    print(f"\n{Colors.BLUE}=== REFLEX CONFIG ==={Colors.RESET}")
    
    try:
        with open('rxconfig.py', 'r') as f:
            content = f.read()
            
        has_include_dirs = 'include_directories' in content
        print_status('include_directories', has_include_dirs, 
                    "Configured to include backend" if has_include_dirs else "NOT configured - backend may be excluded!")
        
        has_api_url = 'REFLEX_API_URL' in content
        print_status('REFLEX_API_URL', has_api_url, 
                    "Configured for deployment" if has_api_url else "Not configured")
        
        return has_include_dirs and has_api_url
    except Exception as e:
        print_status('rxconfig.py check', False, f"Error reading config: {e}")
        return False

def check_backend_imports():
    """Test if backend imports work."""
    print(f"\n{Colors.BLUE}=== BACKEND IMPORTS ==={Colors.RESET}")
    
    all_import = True
    try:
        from backend.recommender import get_combined_recommendations
        print_status('backend.recommender', True, "Imports successfully")
    except Exception as e:
        print_status('backend.recommender', False, f"Import failed: {e}")
        all_import = False
    
    try:
        from backend.rating_based import get_rating_based_recommendations
        print_status('backend.rating_based', True, "Imports successfully")
    except Exception as e:
        print_status('backend.rating_based', False, f"Import failed: {e}")
        all_import = False
    
    try:
        from backend.collaborative_filtering import get_collaborative_recommendations
        print_status('backend.collaborative_filtering', True, "Imports successfully")
    except Exception as e:
        print_status('backend.collaborative_filtering', False, f"Import failed: {e}")
        all_import = False
    
    try:
        from backend.content_filtering import get_content_based_recommendations
        print_status('backend.content_filtering', True, "Imports successfully")
    except Exception as e:
        print_status('backend.content_filtering', False, f"Import failed: {e}")
        all_import = False
    
    return all_import

def check_gitignore():
    """Check if .gitignore is properly configured."""
    print(f"\n{Colors.BLUE}=== .GITIGNORE CONFIGURATION ==={Colors.RESET}")
    
    try:
        with open('.gitignore', 'r') as f:
            content = f.read()
        
        has_env = '.env' in content
        print_status('.env in .gitignore', has_env, 
                    "Correct - .env should not be committed" if has_env else "WRONG - .env should be ignored")
        
        has_pycache = '__pycache__' in content
        print_status('__pycache__ in .gitignore', has_pycache, "Correct")
        
        # Backend should NOT be in gitignore
        has_backend_ignored = 'backend/' in content or '^backend' in content
        print_status('backend/ NOT ignored', not has_backend_ignored, 
                    "Correct - backend will be deployed" if not has_backend_ignored else "WRONG - backend is ignored!")
        
        return has_env and has_pycache and not has_backend_ignored
    except Exception as e:
        print_status('.gitignore check', False, f"Error reading .gitignore: {e}")
        return False

def main():
    """Run all checks."""
    print(f"\n{Colors.BLUE}╔════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║  REFLEX DEPLOYMENT VALIDATION SCRIPT   ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚════════════════════════════════════════╝{Colors.RESET}")
    print(f"\nChecking if your app is ready for: {Colors.YELLOW}reflex deploy{Colors.RESET}\n")
    
    results = {
        'Backend Files': check_backend_files(),
        'Frontend Files': check_frontend_files(),
        'Data Files': check_data_files(),
        'Config Files': check_config_files(),
        'Environment Configuration': check_env_configuration(),
        'Reflex Config': check_rxconfig(),
        'Backend Imports': check_backend_imports(),
        '.gitignore Setup': check_gitignore(),
    }
    
    # Summary
    print(f"\n{Colors.BLUE}=== SUMMARY ==={Colors.RESET}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        symbol = f"{Colors.GREEN}✓{Colors.RESET}" if result else f"{Colors.RED}✗{Colors.RESET}"
        print(f"{symbol} {check}")
    
    print(f"\n{Colors.BLUE}Result: {passed}/{total} checks passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}✓ All checks passed! You can now run: reflex deploy{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}⚠ Fix the issues above before running: reflex deploy{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
