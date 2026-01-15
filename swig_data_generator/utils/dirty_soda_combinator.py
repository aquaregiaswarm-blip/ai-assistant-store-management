"""
Dirty Soda Combinator - Menu Logic Generator
Uses Conditional Probability Tables (CPT) to generate realistic drink customizations.
Implements the "70% dirty ratio" - most drinks at Swig have modifiers.
"""

import numpy as np
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class LineItem:
    """Represents a line item in an order."""
    sku: str
    name: str
    item_type: str
    quantity: int
    unit_price: float
    parent_sku: Optional[str] = None
    modifier_group: Optional[str] = None


class DirtySodaCombinator:
    """Generates realistic drink orders with modifiers based on Swig patterns."""

    def __init__(self, config_path: str = None, seed: int = None):
        if seed:
            np.random.seed(seed)

        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'probability_tables.yaml'

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Product catalog (simplified - would load from DB in production)
        self.products = self._load_product_catalog()

        # Dirty ratio - 70% of base drinks get modifiers
        self.dirty_ratio = 0.70

        # Signature drinks already have modifiers baked in
        self.signature_skus = [f'SIG{i:03d}' for i in range(1, 11)]

    def _load_product_catalog(self) -> Dict:
        """Load product catalog with pricing."""
        return {
            # Signature Drinks
            'SIG001': {'name': 'Texas Tab', 'type': 'Base_Beverage', 'price': 4.29},
            'SIG002': {'name': 'Raspberry Dream', 'type': 'Base_Beverage', 'price': 4.29},
            'SIG003': {'name': 'Island Dream', 'type': 'Base_Beverage', 'price': 4.29},
            'SIG004': {'name': 'The Founder', 'type': 'Base_Beverage', 'price': 4.29},
            'SIG005': {'name': 'Dirty Dr Pepper', 'type': 'Base_Beverage', 'price': 3.99},
            'SIG006': {'name': 'Miami Vice', 'type': 'Base_Beverage', 'price': 4.29},
            'SIG007': {'name': 'The Refresher', 'type': 'Base_Beverage', 'price': 4.49},
            'SIG008': {'name': 'Peach Ring', 'type': 'Base_Beverage', 'price': 4.29},
            'SIG009': {'name': 'Blue Coconut', 'type': 'Base_Beverage', 'price': 4.29},
            'SIG010': {'name': 'Sunset', 'type': 'Base_Beverage', 'price': 4.29},
            # Base Sodas
            'BASE001': {'name': 'Dr Pepper', 'type': 'Base_Beverage', 'price': 2.99},
            'BASE002': {'name': 'Diet Dr Pepper', 'type': 'Base_Beverage', 'price': 2.99},
            'BASE003': {'name': 'Coca-Cola', 'type': 'Base_Beverage', 'price': 2.99},
            'BASE004': {'name': 'Diet Coke', 'type': 'Base_Beverage', 'price': 2.99},
            'BASE005': {'name': 'Sprite', 'type': 'Base_Beverage', 'price': 2.99},
            'BASE006': {'name': 'Sprite Zero', 'type': 'Base_Beverage', 'price': 2.99},
            'BASE007': {'name': 'Mountain Dew', 'type': 'Base_Beverage', 'price': 2.99},
            'BASE008': {'name': 'Diet Mountain Dew', 'type': 'Base_Beverage', 'price': 2.99},
            'BASE009': {'name': 'Lemonade', 'type': 'Base_Beverage', 'price': 3.29},
            'BASE010': {'name': 'Water', 'type': 'Base_Beverage', 'price': 1.99},
            # Energy
            'ENG001': {'name': 'Reviver Original', 'type': 'Base_Beverage', 'price': 4.99},
            'ENG002': {'name': 'Reviver Tropical', 'type': 'Base_Beverage', 'price': 4.99},
            'ENG003': {'name': 'Reviver Berry', 'type': 'Base_Beverage', 'price': 4.99},
            'ENG004': {'name': 'Reviver Sugar Free', 'type': 'Base_Beverage', 'price': 4.99},
            # Modifiers - Creams
            'MOD001': {'name': 'Coconut Cream', 'type': 'Modifier', 'price': 0.79, 'group': 'Cream'},
            'MOD002': {'name': 'Half & Half Cream', 'type': 'Modifier', 'price': 0.79, 'group': 'Cream'},
            'MOD003': {'name': 'Heavy Cream', 'type': 'Modifier', 'price': 0.89, 'group': 'Cream'},
            'MOD004': {'name': 'Oat Milk', 'type': 'Modifier', 'price': 0.99, 'group': 'Cream'},
            'MOD005': {'name': 'Almond Milk', 'type': 'Modifier', 'price': 0.99, 'group': 'Cream'},
            # Modifiers - Syrups
            'SYR001': {'name': 'Vanilla Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR002': {'name': 'Raspberry Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR003': {'name': 'Coconut Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR004': {'name': 'Peach Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR005': {'name': 'Mango Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR006': {'name': 'Strawberry Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR007': {'name': 'Blue Raspberry Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR008': {'name': 'Cherry Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR009': {'name': 'Lime Syrup', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR010': {'name': 'Sugar Free Vanilla', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR011': {'name': 'Sugar Free Raspberry', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            'SYR012': {'name': 'Sugar Free Coconut', 'type': 'Modifier', 'price': 0.69, 'group': 'Syrup'},
            # Modifiers - Purees
            'PUR001': {'name': 'Raspberry Puree', 'type': 'Modifier', 'price': 0.89, 'group': 'Puree'},
            'PUR002': {'name': 'Peach Puree', 'type': 'Modifier', 'price': 0.89, 'group': 'Puree'},
            'PUR003': {'name': 'Strawberry Puree', 'type': 'Modifier', 'price': 0.89, 'group': 'Puree'},
            'PUR004': {'name': 'Mango Puree', 'type': 'Modifier', 'price': 0.89, 'group': 'Puree'},
            'PUR005': {'name': 'Pineapple Puree', 'type': 'Modifier', 'price': 0.89, 'group': 'Puree'},
            # Modifiers - Other
            'ADD001': {'name': 'Fresh Lime', 'type': 'Modifier', 'price': 0.49, 'group': 'Fresh'},
            'ADD002': {'name': 'Fresh Lemon', 'type': 'Modifier', 'price': 0.49, 'group': 'Fresh'},
            'ADD003': {'name': 'Energy Shot', 'type': 'Modifier', 'price': 1.49, 'group': 'Boost'},
            'ADD004': {'name': 'Extra Ice', 'type': 'Modifier', 'price': 0.00, 'group': 'Ice'},
            'ADD005': {'name': 'Light Ice', 'type': 'Modifier', 'price': 0.00, 'group': 'Ice'},
            # Food
            'FOOD001': {'name': 'Sugar Cookie', 'type': 'Food', 'price': 2.49},
            'FOOD002': {'name': 'Chocolate Chip Cookie', 'type': 'Food', 'price': 2.49},
            'FOOD003': {'name': 'Pretzel Bites', 'type': 'Food', 'price': 4.29},
            'FOOD004': {'name': 'Cookie Dough Bites', 'type': 'Food', 'price': 3.99},
            'FOOD005': {'name': 'Brownie', 'type': 'Food', 'price': 2.99},
        }

    def select_base_drink(self) -> str:
        """Select a base drink based on popularity distribution."""
        probs = self.config['base_drink_probabilities']
        skus = list(probs.keys())
        weights = list(probs.values())

        # Normalize weights
        total = sum(weights)
        weights = [w / total for w in weights]

        return np.random.choice(skus, p=weights)

    def select_modifiers(self, base_sku: str) -> List[str]:
        """Select modifiers for a base drink using conditional probabilities."""
        # Signature drinks come pre-made, no additional modifiers usually
        if base_sku in self.signature_skus:
            # 20% chance of extra modifiers even on signature drinks
            if np.random.random() > 0.20:
                return []

        # Check if we're making it "dirty"
        if np.random.random() > self.dirty_ratio:
            return []  # Plain drink

        modifiers = []
        modifier_probs = self.config.get('modifier_given_base', {}).get(base_sku, {})

        if not modifier_probs:
            # Default modifier probabilities for drinks without specific rules
            modifier_probs = {
                'MOD001': 0.40,  # Coconut Cream (most popular)
                'SYR001': 0.20,  # Vanilla
                'ADD001': 0.15,  # Fresh Lime
            }

        # Roll for each modifier
        for mod_sku, prob in modifier_probs.items():
            if np.random.random() < prob:
                modifiers.append(mod_sku)

        # Limit to max 3 modifiers per drink (realistic)
        if len(modifiers) > 3:
            modifiers = list(np.random.choice(modifiers, size=3, replace=False))

        return modifiers

    def select_food_item(self, time_period: str) -> Optional[str]:
        """Select a food item based on time period and attachment rates."""
        food_config = self.config['food_attachment_rates'].get(time_period, {})
        attach_rate = food_config.get('rate', 0.15)

        if np.random.random() > attach_rate:
            return None

        # Select which food item
        food_items = {k: v for k, v in food_config.items() if k.startswith('FOOD')}
        if not food_items:
            return None

        skus = list(food_items.keys())
        weights = list(food_items.values())
        total = sum(weights)
        weights = [w / total for w in weights]

        return np.random.choice(skus, p=weights)

    def generate_order(self, time_period: str = 'afternoon') -> List[LineItem]:
        """
        Generate a complete order with drinks, modifiers, and optional food.

        Args:
            time_period: Time of day ('morning', 'lunch', 'after_school', 'evening')

        Returns:
            List of LineItem objects representing the order
        """
        items = []

        # Determine number of drinks in this order
        items_dist = self.config['items_per_order']
        num_drinks = int(np.random.choice(
            list(map(int, items_dist.keys())),
            p=list(items_dist.values())
        ))

        for _ in range(num_drinks):
            # Select base drink
            base_sku = self.select_base_drink()
            base_product = self.products[base_sku]

            items.append(LineItem(
                sku=base_sku,
                name=base_product['name'],
                item_type=base_product['type'],
                quantity=1,
                unit_price=base_product['price']
            ))

            # Select modifiers for this drink
            modifiers = self.select_modifiers(base_sku)
            for mod_sku in modifiers:
                mod_product = self.products[mod_sku]
                items.append(LineItem(
                    sku=mod_sku,
                    name=mod_product['name'],
                    item_type=mod_product['type'],
                    quantity=1,
                    unit_price=mod_product['price'],
                    parent_sku=base_sku,
                    modifier_group=mod_product.get('group', 'Other')
                ))

        # Check for food attachment
        food_sku = self.select_food_item(time_period)
        if food_sku:
            food_product = self.products[food_sku]
            items.append(LineItem(
                sku=food_sku,
                name=food_product['name'],
                item_type=food_product['type'],
                quantity=1,
                unit_price=food_product['price']
            ))

        return items

    def calculate_order_total(self, items: List[LineItem]) -> Tuple[float, float, float]:
        """
        Calculate order totals.

        Returns:
            Tuple of (subtotal, tax, total)
        """
        subtotal = sum(item.unit_price * item.quantity for item in items)
        tax_rate = 0.0725  # Utah sales tax
        tax = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax, 2)

        return subtotal, tax, total


def generate_vehicle_descriptor() -> str:
    """Generate a random vehicle description for drive-thru orders."""
    colors = ['Red', 'Blue', 'White', 'Black', 'Silver', 'Gray', 'Green', 'Gold', 'Tan', 'Brown']
    makes = ['Honda', 'Toyota', 'Ford', 'Chevy', 'Nissan', 'Hyundai', 'Kia', 'Subaru', 'Tesla', 'Jeep', 'Dodge', 'GMC']
    models = {
        'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot'],
        'Toyota': ['Camry', 'Corolla', 'RAV4', 'Tacoma', '4Runner'],
        'Ford': ['F-150', 'Explorer', 'Mustang', 'Escape'],
        'Chevy': ['Silverado', 'Equinox', 'Malibu', 'Tahoe'],
        'Nissan': ['Altima', 'Rogue', 'Sentra', 'Frontier'],
        'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe'],
        'Kia': ['Sorento', 'Sportage', 'Forte', 'Telluride'],
        'Subaru': ['Outback', 'Forester', 'Crosstrek', 'Impreza'],
        'Tesla': ['Model 3', 'Model Y', 'Model S', 'Model X'],
        'Jeep': ['Wrangler', 'Cherokee', 'Grand Cherokee', 'Compass'],
        'Dodge': ['Ram', 'Durango', 'Charger', 'Challenger'],
        'GMC': ['Sierra', 'Yukon', 'Terrain', 'Canyon'],
    }

    color = np.random.choice(colors)
    make = np.random.choice(makes)
    model = np.random.choice(models.get(make, ['Sedan']))

    return f"{color} {make} {model}"
