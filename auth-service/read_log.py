try:
    with open(r"d:\digital-book\auth-service\startup_nobody.log", "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
        if "Stack:" in content:
            print("--- STACK TRACE ---")
            print(content.split("Stack:")[1][:1000])
        else:
            print("Stack trace not found. Full content:")
            print(content[-500:])
except Exception as e:
    print(f"Error reading log: {e}")
