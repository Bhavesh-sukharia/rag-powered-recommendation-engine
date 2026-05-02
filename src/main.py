def main():
    print("Environment verification script")
    try:
        import sys
        import numpy as np
        import pandas as pd
        import sklearn
        print(f"Python: {sys.version.split()[0]}")
        print(f"numpy: {np.__version__}")
        print(f"pandas: {pd.__version__}")
        print(f"scikit-learn: {sklearn.__version__}")
        print("OK: core packages import successfully.")
    except Exception as e:
        print("Error importing core packages:", e)

if __name__ == '__main__':
    main()
