// Clean version of soil-therapy.js with new color logic - 25% tolerance

// New color logic for nutrient bars - 25% tolerance
function getBarColor(value, min, max) {
    const lower = min * 0.75;  // 25% below min
    const upper = max * 1.25;  // 25% above max
    
    console.log(`Color calculation: value=${value}, min=${min}, max=${max}, lower=${lower}, upper=${upper}`);
    
    if (value >= lower && value <= upper) {
        console.log(`Result: GREEN (acceptable)`);
        return "#339966"; // green
    } else {
        console.log(`Result: RED (outside range)`);
        return "#ff0000"; // red
    }
}

// Post-processing function to assign frontendStatus for bar coloring
// Usage: applyFrontendTolerance(nutrientsArray)
// Each nutrient object should have: name, value, acceptableMin, acceptableMax
function applyFrontendTolerance(nutrients) {
  nutrients.forEach(nutrient => {
    const min = parseFloat(nutrient.acceptableMin);
    const max = parseFloat(nutrient.acceptableMax);
    const value = parseFloat(nutrient.value);
    if (isNaN(min) || isNaN(max) || isNaN(value)) {
      nutrient.frontendStatus = nutrient.status || "acceptable";
      return;
    }
    
    // Use the new 25% tolerance logic
    const lower = min * 0.75;
    const upper = max * 1.25;
    
    if (value >= lower && value <= upper) {
      nutrient.frontendStatus = "acceptable";
    } else {
      nutrient.frontendStatus = value < lower ? "deficient" : "excessive";
    }
  });
}

// Call applyFrontendTolerance(nutrientsArray) before rendering bars and use nutrient.frontendStatus for color 