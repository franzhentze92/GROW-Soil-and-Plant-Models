def convert_to_kg_ha(value, unit, density=1, application_rate=1):
    """
    Convert different units to kg/ha.
    :param value: The input value
    :param unit: The unit type
    :param density: The density of the substance in kg/L (default is 1 for water-based solutions)
    :param application_rate: The water application rate in L/Ha for dilution-based units (default is 1)
    :return: Converted value in kg/Ha
    """
    conversion_factors = {
        'L/Ha': lambda v: v * density,
        'L/Acre': lambda v: v * density * 2.471,
        'g/Ha': lambda v: v / 1000,
        'mg/Ha': lambda v: v / 1_000_000,
        'g/Acre': lambda v: (v / 1000) * 2.471,
        'mg/Acre': lambda v: (v / 1_000_000) * 2.471,
        'Ton/Ha': lambda v: v * 1000,
        'Ton/Acre': lambda v: v * 2471,
        'mL/Ha': lambda v: (v * density) / 1000,
        'mL/Acre': lambda v: (v * density) * 2.471 / 1000,
        'mL/100L Water': lambda v: (v * density * application_rate) / 100_000,
        'mL/10L Water': lambda v: (v * density * application_rate) / 10_000,
        'g/10L Water': lambda v: (v * application_rate) / 10_000,
        'g/100L Water': lambda v: (v * application_rate) / 100_000,
        'L/10L Water': lambda v: (v * density * application_rate) / 10_000,
        'kg/10L Water': lambda v: (v * application_rate) / 10_000,
        'L/100L Water': lambda v: (v * density * application_rate) / 100_000,
        'kg/100L Water': lambda v: (v * application_rate) / 100_000,
        'Kg/Ha': lambda v: v, # added this since we run the function on all products,
        'L of product per L of water': lambda v: (v * density * application_rate) / 1_000
    }

    try:
        # if unit in conversion_factors:
        return conversion_factors[unit](value)
    except Exception as e:
        # else:
        return ValueError("Unit not recognized. Please use a supported unit. ", e)

# # Example usage
# if __name__ == "__main__":
#     # User inputs
#     # value = float(input("Enter value: "))
#     # unit = input("Enter unit: ")
#     # density = float(input("Enter density (kg/L, default=1): ") or 1)
#     # application_rate = float(input("Enter application rate (L/Ha, default=1): ") or 1)
    
#     value = 1               # rate
#     unit = 'L/Ha'           # unit
#     density = 1             # from density file
#     application_rate = 1    # L of water (new input), need to collect that from the front-end and the data will be in Liters

#     result = convert_to_kg_ha(value, unit, density, application_rate)
#     print(f"Converted value: {result} kg/Ha")
#     # try:
#     # except ValueError as e:
#     #     print(e)