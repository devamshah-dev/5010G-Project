import math
from src.microservice_catalog import MicroserviceCatalog
from src.microservice_model import Microservice

class CompositionSimulator:

    #Simulates the aggregated QoS and Cost for a composite service based on selected individual microservices.

    def __init__(self, microservice_catalog: MicroserviceCatalog):
        self.catalog = microservice_catalog

    def calculate_composite_metrics(self, selected_microservice_ids: list[str]) -> dict:

        #finds aggregated QoS and total Cost for a given list of selected microservice IDs.
        # 'series' composition for latency and availability degradation, summation for cost. 
        # Throughput might be bottlenecked by the lowest.
        
        selected_services: list[Microservice] = []
        for ms_id in selected_microservice_ids:
            ms = self.catalog.get_microservice_by_id(ms_id)
            if ms:
                selected_services.append(ms)
            else:
                print(f"Warning: Microservice with ID '{ms_id}' not found in catalog. Skipping.")
                # You might want to assign a very high penalty cost/low QoS here
                # to discourage the GA from picking invalid services.
                # For simplicity in this demo, we just skip.

        if not selected_services:
            # If no valid services are selected, return "worst case" metrics
            return {
                'total_cost': float('inf'),
                'total_latency_ms': float('inf'),
                'total_availability_percent': 0.0,
                'min_throughput_rps': 0.0
            }

        # Initialize aggregate metrics
        total_cost = 0.0
        total_latency_ms = 0.0
        total_availability_product = 1.0 # For availability in series (multiplied)
        min_throughput_rps = float('inf') # Bottleneck for throughput

        for ms in selected_services:
            total_cost += (ms.cost_per_request * 1000) + ms.fixed_hourly_cost # assuming 1000 requests per hour for per-request cost
            total_latency_ms += ms.base_latency_ms
            total_availability_product *= (ms.base_availability_percent / 100.0) # Convert to decimal for multiplication
            min_throughput_rps = min(min_throughput_rps, ms.base_throughput_rps)

        # convert back availability to percentage
        total_availability_percent = total_availability_product * 100.0

        return {
            'total_cost': total_cost,
            'total_latency_ms': total_latency_ms,
            'total_availability_percent': total_availability_percent,
            'min_throughput_rps': min_throughput_rps
        }

if __name__ == "__main__":
    catalog = MicroserviceCatalog()
    simulator = CompositionSimulator(catalog)

    #Compose a simple service (Auth V1 + Payment Stripe)
    composition_ids_1 = ["auth-v1", "payment-stripe"]
    metrics_1 = simulator.calculate_composite_metrics(composition_ids_1)
    print("\n--- Composition 1 Metrics (Auth V1 + Payment Stripe) ---")
    print(json.dumps(metrics_1, indent=2))

    #Compose a more performant service (Auth V2 + NoSQL Pro)
    composition_ids_2 = ["auth-v2", "db-nosql-pro"]
    metrics_2 = simulator.calculate_composite_metrics(composition_ids_2)
    print("\n--- Composition 2 Metrics (Auth V2 + NoSQL Pro) ---")
    print(json.dumps(metrics_2, indent=2))

    #Invalid IDs
    composition_ids_3 = ["non-existent-id", "auth-v1"]
    metrics_3 = simulator.calculate_composite_metrics(composition_ids_3)
    print("\n--- Composition 3 Metrics (Invalid ID + Auth V1) ---")
    print(json.dumps(metrics_3, indent=2))