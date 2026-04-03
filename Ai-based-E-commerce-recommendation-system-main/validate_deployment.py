#!/usr/bin/env python
"""
Deployment Validation Script
Verifies all backend files, imports, and configuration for deployment.
"""

import os
import sys
from pathlib import Path

def check_backend_files():
    """Check if all backend files exist."""
    print("🔍 Checking backend files...")
    backend_files = [
        'backend/__init__.py',
        'backend/recommender.py',
        'backend/collaborative_filtering.py',
        'backend/content_filtering.py',
        'backend/rating_based.py',
        'backend/cleaning_data.py',
    ]
    
    missing = []
    for file in backend_files:
        if not os.path.exists(file):
            missing.append(file)
            print(f"  ❌ {file}")
        else:
            print(f"  ✅ {file}")
    
    return len(missing) == 0

def check_data_files():
    """Check if data files exist."""
    print("\n📊 Checking data files...")
    data_files = ['cleaned_data.csv', 'clean_data.csv']
    
    found = False
    for file in data_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
            found = True
        else:
            print(f"  ⚠️  {file} not found")
    
    if not found:
        print("  ⚠️  WARNING: No CSV data files found. Recommendations will fail.")
    
    return found

def check_imports():
    """Test if backend imports work."""
    print("\n🔗 Checking imports...")
    try:
        from backend.recommender import get_combined_recommendations
        print("  ✅ backend.recommender imports successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import backend.recommender: {e}")
        return False
    
    try:
        from backend.rating_based import get_rating_based_recommendations
        print("  ✅ backend.rating_based imports successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import backend.rating_based: {e}")
        return False
    
    try:
        from backend.collaborative_filtering import get_collaborative_recommendations
        print("  ✅ backend.collaborative_filtering imports successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import backend.collaborative_filtering: {e}")
        return False
    
    try:
        from backend.content_filtering import get_content_based_recommendations
        print("  ✅ backend.content_filtering imports successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import backend.content_filtering: {e}")
        return False
    
    return True

def check_env_vars():
    """Check if environment variables are properly configured."""
    print("\n🔐 Checking environment variables...")
    
    required_vars = [
        'FIREBASE_API_KEY',
        'FIREBASE_PROJECT_ID',
        'GROQ_API_KEY',
    ]
    
    optional_vars = [
        'RAZORPAY_KEY_ID',
        'RAZORPAY_KEY_SECRET',
    ]
    
    print("  Required variables:")
    missing_required = []
    for var in required_vars:
        if os.environ.get(var):
            print(f"    ✅ {var} is set")
        else:
            print(f"    ⚠️  {var} is NOT set (will cause issues on deploy)")
            missing_required.append(var)
    
    print("  Optional variables:")
    for var in optional_vars:
        if os.environ.get(var):
            print(f"    ✅ {var} is set")
        else:
            print(f"    ⚠️  {var} is NOT set")
    
    return len(missing_required) == 0

def check_gitignore():
    """Check .gitignore for critical files."""
    print("\n📋 Checking .gitignore...")
    
    with open('.gitignore', 'r') as f:
        gitignore_content = f.read()
    
    if '\.env\n' in gitignore_content or '.env' in gitignore_content:
        print("  ✅ .env is properly in .gitignore (good for security)")
    else:
        print("  ⚠️  .env is NOT in .gitignore (SECURITY RISK)")
    
    if 'backend' not in gitignore_content:
        print("  ✅ backend/ is NOT ignored (will be deployed)")
    else:
        print("  ❌ backend/ is in .gitignore (CRITICAL: won't be deployed)")
        return False
    
    return True

def main():
    """Run all checks."""
    print("=" * 50)
    print("🚀 AI-Store Deployment Validation")
    print("=" * 50)
    
    checks = [
        ("Backend files exist", check_backend_files),
        ("Data files exist", check_data_files),
        ("Imports work", check_imports),
        ("Environment variables", check_env_vars),
        (".gitignore is correct", check_gitignore),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"  ❌ Error during check: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All checks passed! Ready for deployment.")
    else:
        print("❌ Some checks failed. See above for details.")
        print("\n📝 Next steps:")
        print("1. Fix any failed checks")
        print("2. Set environment variables on deployment platform")
        print("3. Ensure cleaned_data.csv is included in deployment")
        print("4. Read DEPLOYMENT.md for platform-specific instructions")
    
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
