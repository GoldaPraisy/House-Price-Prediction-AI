import sys
try:
    import pandas as pd
    import numpy as np
    import sklearn
    import flask
    import flask_cors
    import joblib
    print("SUCCESS: pandas, numpy, sklearn, flask, flask_cors, joblib are all installed!")
except Exception as e:
    print(f"ERROR: {e}")
