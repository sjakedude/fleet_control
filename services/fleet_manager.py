"""Fleet management service"""


class FleetManager:
    """Manages fleet data and operations"""

    def __init__(self):
        """Initialize the fleet manager"""
        self.vehicles = []

    def add_vehicle(self, vehicle):
        """Add a vehicle to the fleet"""
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle_id):
        """Remove a vehicle from the fleet"""
        self.vehicles = [v for v in self.vehicles if v.id != vehicle_id]

    def get_all_vehicles(self):
        """Get all vehicles in the fleet"""
        return self.vehicles
