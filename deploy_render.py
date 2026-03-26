#!/usr/bin/env python3
"""
Render Backend Deployment Script
Deploys ml-evaluator backend to Render platform
"""
import requests
import json
import time
import sys

API_KEY = "rnd_3btb3u8Fi5MipRrfxIdafZtHO07P"
OWNER_ID = "tea-d6rt2f7afjfc73ekrijg"
API_HOST = "https://api.render.com/v1/"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def deploy_service():
    """Deploy service to Render"""
    print("\n" + "="*70)
    print("🚀 DEPLOYING ML EVALUATOR BACKEND TO RENDER")
    print("="*70)
    
    payload = {
        "name": "ml-evaluator-backend",
        "ownerId": OWNER_ID,
        "type": "web_service",
        "repo": "https://github.com/2022509542chaman-bit/INTERVIEW-SELECTION-VIA-ML-",
        "branch": "main",
        "serviceDetails": {
            "env": "docker",
            "dockerfilePath": "Dockerfile"
        },
        "autoDeploy": True
    }
    
    print("\n📋 Deploying with config:")
    print(json.dumps(payload, indent=2))
    
    try:
        resp = requests.post(
            f"{API_HOST}services",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"\n📡 Response Status: {resp.status_code}")
        
        if resp.status_code == 402:
            print("\n⚠️  PAYMENT REQUIRED")
            print("\nRender requires a payment method on file before deployment.")
            print("This is needed even for free tier services.\n")
            print("ACTION REQUIRED:")
            print("1. Go to: https://dashboard.render.com/billing")
            print("2. Click 'Add Payment Method'")
            print("3. Enter credit card details")
            print("4. Save")
            print("\nAfter adding payment, rerun this script or:")
            print("5. Go to: https://dashboard.render.com")
            print("6. Click 'New +' → 'Web Service'")
            print("7. Connect GitHub repo")
            print("8. Render auto-detects render.yaml → Deploy\n")
            return False
            
        elif resp.status_code in [200, 201]:
            service = resp.json()
            print("\n✅ SERVICE DEPLOYED SUCCESSFULLY!")
            print(f"\nService ID: {service.get('id')}")
            print(f"Name: {service.get('name')}")
            print(f"Status: {service.get('status')}")
            
            service_id = service['id']
            with open("/tmp/render_service_id.txt", "w") as f:
                f.write(service_id)
            
            print("\n⏳ Build Status: Initializing...")
            print("(First build: 10-15 minutes for ML models)")
            print(f"\n📊 Monitor progress at:")
            print(f"   https://dashboard.render.com/services/{service_id}")
            return True
        else:
            print(f"Error: {resp.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def get_service_status(service_id):
    """Check service status"""
    try:
        resp = requests.get(
            f"{API_HOST}services/{service_id}",
            headers=headers,
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error checking status: {e}")
    return None

if __name__ == "__main__":
    success = deploy_service()
    
    if success:
        print("\n" + "="*70)
        print("✨ NEXT STEPS:")
        print("="*70)
        print("\n1. Wait for build to complete (monitor in dashboard)")
        print("2. Once 'Live', copy the Render URL")
        print("3. Update Vercel environment variable VITE_API_URL")
        print("4. Test frontend connection")
        print("\n" + "="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("⚠️  ACTION REQUIRED - Cannot proceed without payment method")
        print("="*70)
        sys.exit(1)
