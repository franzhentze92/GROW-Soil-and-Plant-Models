from cost_calculator import PRODUCT_PRICES
from nutrient_breakdown import PRODUCT_DATA

# Check if keys in PRODUCT_PRICES exist in PRODUCT_DATA
missing_keys = []

for key in PRODUCT_PRICES.keys():
    if key not in PRODUCT_DATA:
        missing_keys.append(key)

print("Missing Keys - Total: ", len(missing_keys) )
print(missing_keys)
