import json

class Microservice:
    def __init__(self, id, name, type, capabilities, base_latency_ms,
                 base_availability_percent, base_throughput_rps,
                 cost_per_request, fixed_hourly_cost):
        self.id = id
        self.name = name
        self.type = type
        self.capabilities = capabilities
        self.base_latency_ms = base_latency_ms
        self.base_availability_percent = base_availability_percent
        self.base_throughput_rps = base_throughput_rps
        self.cost_per_request = cost_per_request
        self.fixed_hourly_cost = fixed_hourly_cost

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "capabilities": self.capabilities,
            "base_latency_ms": self.base_latency_ms,
            "base_availability_percent": self.base_availability_percent,
            "base_throughput_rps": self.base_throughput_rps,
            "cost_per_request": self.cost_per_request,
            "fixed_hourly_cost": self.fixed_hourly_cost
        }

    def __repr__(self):
        return f"Microservice(id='{self.id}', name='{self.name}', type='{self.type}')"

# Example
if __name__ == "__main__":
    ms_data = {
        "id": "test-ms",
        "name": "Test Service",
        "type": "testing",
        "capabilities": ["unit_test"],
        "base_latency_ms": 10,
        "base_availability_percent": 99.9,
        "base_throughput_rps": 100,
        "cost_per_request": 0.001,
        "fixed_hourly_cost": 0.01
    }
    test_ms = Microservice(**ms_data)
    print(test_ms)
    print(test_ms.to_dict())