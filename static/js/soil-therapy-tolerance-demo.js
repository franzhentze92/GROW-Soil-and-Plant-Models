// Soil Therapy Tolerance System Demo
// This file demonstrates how to implement the tolerance system for soil analysis charts

// Tolerance configuration - 50% above and below for all nutrients by default
const nutrientTolerance = new Proxy({}, {
    get: () => ({ below: 0.5, above: 0.5 })
});

// Example: Set specific tolerances for different nutrients
// nutrientTolerance['Calcium'] = { below: 0.3, above: 0.4 }; // 30% below, 40% above
// nutrientTolerance['Magnesium'] = { below: 0.2, above: 0.3 }; // 20% below, 30% above

/**
 * Apply tolerance to a className based on nutrient values
 * @param {string} originalClassName - The original className from calculateProgress
 * @param {string} nutrientName - Name of the nutrient (e.g., 'Calcium', 'Magnesium')
 * @param {number} value - Current nutrient value
 * @param {number} acceptableMin - Minimum acceptable value
 * @param {number} acceptableMax - Maximum acceptable value
 * @returns {string} - Updated className based on tolerance
 */
function applyToleranceToClassName(originalClassName, nutrientName, value, acceptableMin, acceptableMax) {
    const min = parseFloat(acceptableMin);
    const max = parseFloat(acceptableMax);
    const val = parseFloat(value);
    
    if (isNaN(min) || isNaN(max) || isNaN(val)) {
        return originalClassName; // Return original if values are invalid
    }
    
    const tol = nutrientTolerance[nutrientName];
    const greenMin = min * (1 - tol.below);
    const greenMax = max * (1 + tol.above);
    
    console.log(`Tolerance for ${nutrientName}:`, {
        original: { min, max, value: val },
        tolerance: tol,
        adjusted: { greenMin, greenMax }
    });
    
    // Apply tolerance logic
    if (val < greenMin) {
        return "deficient";
    } else if (val > greenMax) {
        return "excessive";
    } else {
        return "acceptable";
    }
}

/**
 * Enhanced calculateProgress function with tolerance support
 * This function wraps the original calculateProgress and applies tolerance
 */
function calculateProgressWithTolerance(tableCategory, nutrientName, value, acceptableMin, acceptableMax, deficientThreshold, excessiveThreshold, tecValue) {
    // First, get the original result from calculateProgress
    const originalResult = calculateProgress(tableCategory, nutrientName, value, acceptableMin, acceptableMax, deficientThreshold, excessiveThreshold, tecValue);
    
    // Apply tolerance to the className
    const newClassName = applyToleranceToClassName(
        originalResult.className, 
        nutrientName, 
        value, 
        acceptableMin, 
        acceptableMax
    );
    
    return {
        percentage: originalResult.percentage,
        className: newClassName
    };
}

/**
 * Post-processing function to assign frontendStatus for bar coloring
 * @param {Array} nutrients - Array of nutrient objects
 */
function applyFrontendTolerance(nutrients) {
    nutrients.forEach(nutrient => {
        const min = parseFloat(nutrient.acceptableMin);
        const max = parseFloat(nutrient.acceptableMax);
        const value = parseFloat(nutrient.value);
        
        if (isNaN(min) || isNaN(max) || isNaN(value)) {
            nutrient.frontendStatus = nutrient.status || "acceptable";
            return;
        }
        
        const tol = nutrientTolerance[nutrient.name];
        const greenMin = min * (1 - tol.below);
        const greenMax = max * (1 + tol.above);
        
        if (value < greenMin) {
            nutrient.frontendStatus = "deficient";
        } else if (value > greenMax) {
            nutrient.frontendStatus = "excessive";
        } else {
            nutrient.frontendStatus = "acceptable";
        }
    });
}

// Example usage:
// 1. Replace calculateProgress calls with calculateProgressWithTolerance
// 2. Or override the original calculateProgress function:

/*
// Override the original calculateProgress function
const originalCalculateProgress = calculateProgress;
calculateProgress = function(tableCategory, nutrientName, value, acceptableMin, acceptableMax, deficientThreshold, excessiveThreshold, tecValue) {
    const result = originalCalculateProgress(tableCategory, nutrientName, value, acceptableMin, acceptableMax, deficientThreshold, excessiveThreshold, tecValue);
    result.className = applyToleranceToClassName(result.className, nutrientName, value, acceptableMin, acceptableMax);
    return result;
};
*/

// Example: How to set up specific tolerances
function setupNutrientTolerances() {
    // Example tolerances - adjust these based on your needs
    nutrientTolerance['Calcium'] = { below: 0.3, above: 0.4 }; // 30% below, 40% above
    nutrientTolerance['Magnesium'] = { below: 0.2, above: 0.3 }; // 20% below, 30% above
    nutrientTolerance['Potassium'] = { below: 0.4, above: 0.5 }; // 40% below, 50% above
    nutrientTolerance['Phosphorus'] = { below: 0.25, above: 0.35 }; // 25% below, 35% above
    nutrientTolerance['Sulfur'] = { below: 0.3, above: 0.4 }; // 30% below, 40% above
    nutrientTolerance['Zinc'] = { below: 0.2, above: 0.3 }; // 20% below, 30% above
    nutrientTolerance['Copper'] = { below: 0.15, above: 0.25 }; // 15% below, 25% above
    nutrientTolerance['Manganese'] = { below: 0.25, above: 0.35 }; // 25% below, 35% above
    nutrientTolerance['Iron'] = { below: 0.2, above: 0.3 }; // 20% below, 30% above
    nutrientTolerance['Boron'] = { below: 0.3, above: 0.4 }; // 30% below, 40% above
    nutrientTolerance['Molybdenum'] = { below: 0.4, above: 0.5 }; // 40% below, 50% above
    nutrientTolerance['Selenium'] = { below: 0.3, above: 0.4 }; // 30% below, 40% above
    nutrientTolerance['Cobalt'] = { below: 0.25, above: 0.35 }; // 25% below, 35% above
    nutrientTolerance['Nickel'] = { below: 0.2, above: 0.3 }; // 20% below, 30% above
    nutrientTolerance['Vanadium'] = { below: 0.3, above: 0.4 }; // 30% below, 40% above
    nutrientTolerance['Chromium'] = { below: 0.25, above: 0.35 }; // 25% below, 35% above
    nutrientTolerance['Aluminum'] = { below: 0.2, above: 0.3 }; // 20% below, 30% above
    nutrientTolerance['Sodium'] = { below: 0.3, above: 0.4 }; // 30% below, 40% above
    nutrientTolerance['Chloride'] = { below: 0.25, above: 0.35 }; // 25% below, 35% above
    nutrientTolerance['Silicon'] = { below: 0.2, above: 0.3 }; // 20% below, 30% above
}

// Color mapping for the tolerance system
const toleranceColors = {
    'deficient': 'red',
    'acceptable': 'rgb(51, 153, 102)', // Green
    'excessive': 'rgb(0, 255, 255)' // Cyan
};

// Example: How to apply colors based on tolerance
function getColorFromTolerance(className) {
    return toleranceColors[className] || 'gray';
}

// Export functions for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        nutrientTolerance,
        applyToleranceToClassName,
        calculateProgressWithTolerance,
        applyFrontendTolerance,
        setupNutrientTolerances,
        toleranceColors,
        getColorFromTolerance
    };
} 