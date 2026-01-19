import sys
import os

def test_dashboard_syntax():
    print("Testing dashboard syntax...")
    dashboard_path = os.path.join("app", "dashboard", "dashboard.py")
    
    if not os.path.exists(dashboard_path):
        print(f"[ERROR] File not found: {dashboard_path}")
        return 1
        
    try:
        # Just compile it to check for syntax errors
        with open(dashboard_path, "r", encoding="utf-8") as f:
            source = f.read()
        compile(source, dashboard_path, "exec")
        print(" [OK] Dashboard syntax valid")
        return 0
    except SyntaxError as e:
        print(f"[ERROR] Syntax error in dashboard: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_dashboard_syntax())
