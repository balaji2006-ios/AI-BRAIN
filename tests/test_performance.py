
from assistant.evaluation.performance import PerformanceMonitor


def test_performance_storage():

    print("\n===== PERFORMANCE STORAGE TEST =====")

    monitor = PerformanceMonitor()

    # Create a sample performance record
    sample_record = {
        "timestamp": "2026-10-31T10:00:00",
        "provider": "Gemini Cloud",
        "status": "Success",
        "response_time": 2.5,
        "ram_before_mb": 30.0,
        "ram_after_mb": 35.0,
        "ram_change_mb": 5.0,
        "session_id": "test-session"
    }

    # Save record
    monitor.save_record(sample_record)

    print("\nPerformance record saved!")

    # Retrieve records
    records = monitor.get_all_records()

    print("\nStored Performance Records:")

    for record in records:
        print(record)

    # Verify the saved record
    assert sample_record in records

    print("\nPerformance Storage Test Successful!")


if __name__ == "__main__":
    test_performance_storage()
