"""
Test script for CTGenie API
Run this after starting the API server with: python main.py
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_health_check():
    """Test the root endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)

    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    return response.status_code == 200


def test_prediction():
    """Test prediction endpoint"""
    print("\n" + "="*60)
    print("TEST 2: NSP Prediction")
    print("="*60)

    # Sample CTG features (normal pattern)
    request_data = {
        "ctg_features": {
            "LB": 135.0,
            "AC": 4.0,
            "FM": 8.0,
            "UC": 5.0,
            "DL": 0.0,
            "DS": 0.0,
            "DP": 0.0,
            "ASTV": 55.0,
            "MSTV": 1.5,
            "ALTV": 12.0,
            "MLTV": 10.0
        },
        "patient_context": {
            "age": 28,
            "gestational_age_weeks": 39.0,
            "gravida": 2,
            "para": 1,
            "risk_factors": []
        }
    }

    print(f"Request: {json.dumps(request_data, indent=2)}")

    response = requests.post(f"{API_URL}/predict", json=request_data)
    print(f"\nStatus: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Prediction: {result['prediction_label']}")
        print(f"✅ Confidence: {result['confidence']:.3f}")
        print(f"\n📊 Probabilities:")
        for cls, prob in result['probabilities'].items():
            print(f"   {cls}: {prob:.3f}")

        if result.get('shap_values'):
            print(f"\n🔍 Top SHAP Features:")
            sorted_shap = sorted(result['shap_values'].items(),
                                key=lambda x: abs(x[1]), reverse=True)
            for feat, val in sorted_shap[:5]:
                print(f"   {feat}: {val:.3f}")

        if result.get('similar_cases'):
            print(f"\n📂 Similar Cases: {len(result['similar_cases'])} found")
            for case in result['similar_cases'][:2]:
                print(f"   - {case['case_id']}: {case['nsp_label']} (similarity: {case['similarity_score']:.3f})")

        if result.get('clinical_recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in result['clinical_recommendations'][:3]:
                print(f"   - {rec}")

        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_similar_cases():
    """Test similar cases endpoint"""
    print("\n" + "="*60)
    print("TEST 3: Similar Cases Retrieval")
    print("="*60)

    request_data = {
        "ctg_features": {
            "LB": 120.0,
            "AC": 2.0,
            "ASTV": 45.0
        },
        "top_k": 3
    }

    response = requests.post(f"{API_URL}/similar-cases", json=request_data)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Found {result['count']} similar cases")
        for case in result['similar_cases']:
            print(f"   - {case['case_id']}: {case['nsp_label']} (score: {case['similarity_score']:.3f})")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def test_guidelines():
    """Test guidelines endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Clinical Guidelines")
    print("="*60)

    category = "variability"
    response = requests.get(f"{API_URL}/guidelines/{category}")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Category: {result['category']}")
        print(f"✅ Guidelines found: {len(result['guidelines'])}")
        if result['guidelines']:
            guideline = result['guidelines'][0]
            print(f"\nSample Guideline:")
            print(f"   ID: {guideline['guideline_id']}")
            print(f"   Title: {guideline['title']}")
        return True
    else:
        print(f"❌ Error: {response.text}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🏥 CTGenie API Test Suite" + "\n")

    tests = [
        ("Health Check", test_health_check),
        ("NSP Prediction", test_prediction),
        ("Similar Cases", test_similar_cases),
        ("Clinical Guidelines", test_guidelines)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Cannot connect to API at {API_URL}")
            print("   Make sure the server is running with: python main.py")
            return
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
