import sys

def test_imports():
    print("Testing imports...")
    try:
        import streamlit
        print(" [OK] streamlit")
        import pandas
        print(" [OK] pandas")
        import plotly
        print(" [OK] plotly")
        import sklearn
        print(" [OK] sklearn")
        import joblib
        print(" [OK] joblib")
        import numpy
        print(" [OK] numpy")
        import kafka
        print(" [OK] kafka-python")
        import faker
        print(" [OK] faker")
        
        # Test app modules
        import app.config
        print(" [OK] app.config")
        import app.database
        print(" [OK] app.database")
        
        print("\nAll imports successful!")
        return 0
    except ImportError as e:
        print(f"\n[ERROR] Missing dependency: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
