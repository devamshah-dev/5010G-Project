import json
import os
import pandas as pd
from src.microservice_model import Microservice

class MicroserviceCatalog:
    def __init__(self, data_file_path='data/simulated_microservices.json'):
        self.data_file_path = data_file_path
        self._load_catalog()

    def _load_catalog(self):
        #loads microservice data from the JSON file.
        current_dir = os.path.dirname(__file__)
        abs_data_path = os.path.join(current_dir, '..', self.data_file_path)

        try:
            with open(abs_data_path, 'r') as f:
                data = json.load(f)
            # store as a DataFrame for efficient lookup and filtering
            self.catalog_df = pd.DataFrame(data)
            self.microservices_by_id = {
                row['id']: Microservice(**row) for index, row in self.catalog_df.iterrows()
            }
            print(f"Loaded {len(self.microservices_by_id)} microservices into catalog.")
        except FileNotFoundError:
            print(f"Error: Microservice data file not found at {abs_data_path}")
            self.microservices_by_id = {}
            self.catalog_df = pd.DataFrame() # Initialize empty DataFrame
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {abs_data_path}")
            self.microservices_by_id = {}
            self.catalog_df = pd.DataFrame()

    def get_microservice_by_id(self, ms_id: str) -> Microservice | None:
        #microservice object by its ID.
        return self.microservices_by_id.get(ms_id)

    def get_microservices_by_type(self, ms_type: str) -> list[Microservice]:
        #list of Microservice objects of a specific type.
        filtered_ids = self.catalog_df[self.catalog_df['type'] == ms_type]['id'].tolist()
        return [self.microservices_by_id[ms_id] for ms_id in filtered_ids]

    def get_all_microservices(self) -> list[Microservice]:
        #list of all Microservice objects.
        return list(self.microservices_by_id.values())

if __name__ == "__main__":
    catalog = MicroserviceCatalog()
    auth_v1 = catalog.get_microservice_by_id("auth-v1")
    if auth_v1:
        print(f"Retrieved: {auth_v1.name}, Latency: {auth_v1.base_latency_ms}ms")
    else:
        print("auth-v1 not found.")

    payment_services = catalog.get_microservices_by_type("payment")
    print("\nPayment Services:")
    for ms in payment_services:
        print(f"- {ms.name} (Cost/Req: {ms.cost_per_request})")

    all_services = catalog.get_all_microservices()
    print(f"\nTotal services in catalog: {len(all_services)}")