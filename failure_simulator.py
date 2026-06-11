def simulate_failure(choice):

    if choice == "cpu":
        return {
            "cpu": 95,
            "memory": 40,
            "network": "UP"
        }

    elif choice == "memory":
        return {
            "cpu": 30,
            "memory": 95,
            "network": "UP"
        }

    elif choice == "network":
        return {
            "cpu": 20,
            "memory": 30,
            "network": "DOWN"
        }

    return None