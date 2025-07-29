from src.microservice_catalog import MicroserviceCatalog
from src.microservice_model import Microservice

class ServiceScenario:

    # defines the requirements for a composite service in the simulation.= capabilitiesfrom the composed microservices.

    def __init__(self, name: str, required_capabilities: list[str], catalog: MicroserviceCatalog):
        self.name = name
        self.required_capabilities = required_capabilities
        self.catalog = catalog
        self.available_options_by_type = self._map_available_options()

    def _map_available_options(self) -> dict[str, list[Microservice]]:

       # maps each required capability to a list of microservices in the catalog that can provide that capability.

        options = {}
        for cap in self.required_capabilities:
            # This logic needs iterate through all services and check their capabilities list
            matching_services = []
            for ms in self.catalog.get_all_microservices():
                if cap in ms.capabilities: # Check if the capability is in the MS's list
                    matching_services.append(ms)
            
            if not matching_services:
                print(f"Warning: No microservices found in catalog for required capability: {cap}")
            options[cap] = matching_services
        return options
    
    def get_options_for_capability(self, capability: str) -> list[Microservice]:
        #returns microservice options for a specific capability.= latency etc.
        return self.available_options_by_type.get(capability, [])
if __name__ == "__main__":
    catalog = MicroserviceCatalog()
    
    # user profile service needs Auth, Payment, and Data Storage = scenario
    user_profile_scenario = ServiceScenario(
        name="User Profile Service",
        required_capabilities=["user_authentication", "process_payment", "data_storage"],
        catalog=catalog
    )

    print(f"\nScenario: {user_profile_scenario.name}")
    print("Required Capabilities:", user_profile_scenario.required_capabilities)

    print("\nAvailable options for 'user_authentication':")
    for ms in user_profile_scenario.get_options_for_capability("user_authentication"):
        print(f"- {ms.name} (ID: {ms.id})")

    print("\nAvailable options for 'data_storage':")
    for ms in user_profile_scenario.get_options_for_capability("data_storage"):
        print(f"- {ms.name} (ID: {ms.id})")