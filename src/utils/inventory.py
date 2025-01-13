

class Inventory:
    def __init__(self, max_slots=9, max_items_per_slot=64):
        """
        Initializes the inventory.
        
        :param max_slots: Maximum number of slots in the inventory.
        :param max_items_per_slot: Maximum number of items each slot can hold.
        """
        self.max_slots = max_slots
        self.max_items_per_slot = max_items_per_slot
        self.items = [{} for i in range(self.max_slots)]  # List to store items and their quantities in insertion order
        self._selected: int = 0

    def add_item(self, item: int, quantity=1):
        """
        Attempts to add an item to the inventory.

        :param item: The name of the item to add.
        :param quantity: The quantity of the item to add.
        :return: True if the item was added successfully, False otherwise.
        """
        for entry in self.items:
            if not entry:
                entry['item'] = item
                entry['quantity'] = 1
                return True
            
            elif entry['item'] == item:
                if entry['quantity'] + quantity <= self.max_items_per_slot:
                    entry['quantity'] += quantity
                    return True

        return False

    def set_slot(self, slot_index: int, item: int, quantity: int):
        """
        Sets a specific slot with the given item and quantity.
        
        :param slot_index: The index of the slot to set.
        :param item: The item to store in the slot.
        :param quantity: The quantity of the item to store.
        :raises ValueError: If the quantity exceeds the maximum items per slot.
        """
        if not (0 <= slot_index < self.max_slots):
            return
        if quantity > self.max_items_per_slot or quantity < 0:
            return
        
        self.items[slot_index] = {"item": item, "quantity": quantity}

    def get_slot(self, slot_index: int):
        """
        Gets the contents of a specific slot. Quantity and Item
        
        :param slot_index: The index of the slot to retrieve.
        :return: A dictionary with the item and quantity, or None if the slot is empty.
        :raises ValueError: If the slot index is out of range.
        """
        if not (0 <= slot_index < self.max_slots):
            return None
        
        if not self.items[slot_index]:
            return -1, -1
        
        return self.items[slot_index]['quantity'], self.items[slot_index]['item']

    def get_slots(self):
        r = []
        for s in range(len(self.items)):
            r.append(self.get_slot(s))
    
    def pick_item(self, val: int):
        """
        Picks one item from the currently selected slot.

        :return: The item type if an item is available, None if the slot is empty.
        """
        current_slot = self.items[self._selected]
        if current_slot and current_slot.get("quantity", 0) >= val:
            current_slot["quantity"] -= val
            if current_slot["quantity"] == 0:
                self.items[self._selected] = {}  # Clear the slot if the quantity reaches 0


    @property
    def selected(self):
        """
        Getter for the selected slot.
        
        :return: The currently selected slot.
        """
        return self._selected

    @selected.setter
    def selected(self, value):
        """
        Setter for the selected slot.
        
        :param value: The new slot to select.
        Adjusts to the closest valid value if out of range.
        """
        if value < 0:
            self._selected = 0
        elif value >= self.max_slots:
            self._selected = self.max_slots - 1
        else:
            self._selected = value

    def scroll(self, direction: int):
        """
        Scrolls the selected slot up or down.
        
        :param direction: The direction to scroll (positive to increment, negative to decrement).
        Wraps around if the end or beginning is reached.
        """
        self._selected = (self._selected + direction) % self.max_slots

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