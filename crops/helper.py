def calculate_relative_max_value(extracted_value, deficient, lower, upper, excessive):
    if extracted_value < deficient:
        return deficient * 6
    elif extracted_value >= deficient and extracted_value <= lower:
        return lower * 3
    elif extracted_value > lower and extracted_value <= upper:
        return (upper - lower) * 3
    elif extracted_value > upper and extracted_value <= excessive:
        return (excessive - upper) * 3
    else:
        return excessive


def calculate_relative_current_value(
    extracted_value, deficient, lower, upper, excessive, relative_max
):
    if extracted_value == "N/A" or extracted_value < deficient:
        return 0
    elif extracted_value <= lower and extracted_value >= deficient:
        return extracted_value
    elif extracted_value > lower and extracted_value <= upper:
        return (relative_max / 3) + extracted_value - lower
    elif extracted_value > upper and extracted_value <= excessive:
        return ((relative_max / 3) * 2) + extracted_value - upper
    else:
        return excessive


def calculate_empty_value(extracted_value, lower):
    if extracted_value < lower and extracted_value > lower / 5:
        return extracted_value
    else:
        return 0


def calculate_relative_chart_value(relative_empty, relative_max, relative_current):
    if relative_empty == 0:
        return relative_max - relative_current
    else:
        return relative_max - relative_empty


def deficient_formula(relative_current, relative_empty, extracted_value):
    if relative_current == 0 and relative_empty == 0 and extracted_value != "N/A":
        return "Extremely Low"
    elif extracted_value == "N/A":
        return "Not Tested"
    else:
        return ""


def calculate_final_values_formula(extracted_values):
    for extracted_value in extracted_values:
        if type(extracted_value["value"]) == str:
            continue
        extracted_value["deficient"] = round(extracted_value["lower"] / 1.5, 1) if extracted_value["lower"] else 0
        extracted_value["excessive"] = round(extracted_value["upper"] * 1.5, 1) if extracted_value["upper"] else 0
        extracted_value["relative_max"] = round(
            calculate_relative_max_value(
                extracted_value["value"] if extracted_value["value"] else 0,
                extracted_value["deficient"] if extracted_value["deficient"] else 0,
                extracted_value["lower"] if extracted_value["lower"] else 0,
                extracted_value["upper"] if extracted_value["upper"] else 0,
                extracted_value["excessive"] if extracted_value["excessive"] else 0,
            ),
            2,
        )
        extracted_value["relative_current"] = round(
            calculate_relative_current_value(
                extracted_value["value"] if extracted_value["value"] else 0,
                extracted_value["deficient"] if extracted_value["deficient"] else 0,
                extracted_value["lower"] if extracted_value["lower"] else 0,
                extracted_value["upper"] if extracted_value["upper"] else 0,
                extracted_value["excessive"] if extracted_value["excessive"] else 0,
                extracted_value["relative_max"] if extracted_value["relative_max"] else 0,
            ),
            2,
        )
        extracted_value["relative_empty"] = round(
            calculate_empty_value(extracted_value["value"], extracted_value["deficient"]),
            2,
        )
        extracted_value["relative_empty"] = round(
            calculate_relative_chart_value(
                extracted_value["relative_empty"], extracted_value["relative_max"], extracted_value["relative_current"]
            ),
            2,
        )

    return extracted_values
