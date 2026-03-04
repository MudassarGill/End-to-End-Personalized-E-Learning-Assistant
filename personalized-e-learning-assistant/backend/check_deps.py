try:
    import motor
    import pymongo
    print(f"Motor Version: {motor.version}")
    print(f"Pymongo Version: {pymongo.version}")
    print("SUCCESS: Dependencies imported correctly!")
except Exception as e:
    print(f"ERROR: {e}")
