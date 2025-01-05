

class Inventory:
    def __init__(self, max_slots=10, max_items_per_slot=64):
        """
        Initializes the inventory.
        
        :param max_slots: Maximum number of slots in the inventory.
        :param max_items_per_slot: Maximum number of items each slot can hold.
        """
        self.max_slots = max_slots
        self.max_items_per_slot = max_items_per_slot
        self.items = []  # List to store items and their quantities in insertion order

    def add_item(self, item: int, quantity=1):
        """
        Attempts to add an item to the inventory.

        :param item: The name of the item to add.
        :param quantity: The quantity of the item to add.
        :return: True if the item was added successfully, False otherwise.
        """
        for entry in self.items:
            if entry['item'] == item:
                if entry['quantity'] + quantity <= self.max_items_per_slot:
                    entry['quantity'] += quantity
                    return True

        if len(self.items) < self.max_slots:
            if quantity <= self.max_items_per_slot:
                self.items.append({"item": item, "quantity": quantity})
                return True
            else:
                return False
        return False


    def __repr__(self):
        """Returns a string representation of the inventory."""
        inventory_str = "Inventory:\n"
        for entry in self.items:
            inventory_str += f"- {entry['item']}: {entry['quantity']}\n"
        return inventory_str.strip()

# Example Usage
if __name__ == "__main__":
    inventory = Inventory(5, 10)  # Inventory with 5 slots, each can hold up to 10 items

    print(inventory.add_item("Sword", 3))  # True
    print(inventory.add_item("Shield", 5))  # True
    print(inventory.add_item("Potion", 10))  # True
    print(inventory.add_item("Arrow", 2))  # True
    print(inventory.add_item("Bow", 1))  # True
    print(inventory.add_item("Helmet", 4))  # False (Inventory is full)
    print(inventory.add_item("Potion", 1))  # False (Exceeds max items per slot)

    print(inventory)  # Inventory:
                      # - Sword: 3
                      # - Shield: 5
                      # - Potion: 10
                      # - Arrow: 2
                      # - Bow: 1