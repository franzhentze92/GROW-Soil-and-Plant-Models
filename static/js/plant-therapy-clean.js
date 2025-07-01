// Clean Plant Therapy JavaScript with tolerance settings integration
// This version reads tolerance settings from localStorage and applies them to Django-provided ideal ranges

// Global variables
let selectedMatchingManagementPaddocks = new Set();
let paddock = {
    'table': '',
    'dataset_processed': {},
    'description': '',
    'fertigation_products': [],
    'foliar_products': [],
    'recommendations': {
        'explanation': '',
        'recommended_products': [],
        'form_data': {}
    }
};
let userData = {
    'date': '',
    'name': '',
    'address': '',
    'land': '',
    'sample_rec': '',
    'email': ''
};
let report = {};

// Initialize report
report['title'] = 'Plant Therapy Report';
report['user'] = userData;
report['include_breakdown_price'] = false;
report['include_nutrients_explanation'] = false;
report['description'] = 'Plant Therapy Report';
report['leafCrop'] = null;
report['leafCropGroup'] = null;
report['plantLabType'] = null;

let PRODUCT_PRICES = {};
let CONVERSION_FACTORS = {};
let AREA_CONVERSION_FACTORS = {};
let selectedProducts = {};
report['sample_paddock_farm_assignments'] = [];
report['paddocks'] = {};
report['farmsManagementData'] = {};
let farmsManagementData = {};

// Nutrient antagonism mapping
const nutrient_antagonism = {
    'nitrogen': ['calcium (Ca)', 'magnesium (Mg)', 'potassium (K)', 'boron (B)', 'boron (B)'],
    'phosphorus': ['potassium (K)', 'magnesium (Mg)', 'nitrogen (N)', 'zinc (Zn)', 'zinc (Zn)'],
    'potassium': ['magnesium (Mg)', 'magnesium (Mg)', 'calcium (Ca)', 'nitrogen (N)'],
    'calcium': ['boron (B)', 'nitrogen (N)', 'phosphorus (P)', 'potassium (K)', 'magnesium (Mg)', 'zinc (Zn)', 'nitrogen (N)'],
    'magnesium': ['nitrogen (N)', 'magnesium (Mg)'],
    'iron': ['magnesium (Mg)', 'boron (B)', 'potassium (K)', 'nitrogen (N)', 'phosphorus (P)'],
    'manganese': ['magnesium (Mg)', 'zinc (Zn)', 'potassium (K)'],
    'zinc': ['nitrogen (N)', 'magnesium (Mg)', 'iron (Fe)'],
    'copper': ['manganese (Mn)', 'zinc (Zn)', 'nitrogen (N)', 'nitrogen (N)'],
    'boron': ['nitrogen (N)', 'calcium (Ca)', 'molybdenum (Mo)'],
    'molybdenum': ['copper (Cu)']
};

/**
 * Get bar color based on tolerance settings
 * This function reads tolerance settings from localStorage and applies them to Django-provided ideal ranges
 */
function getBarColor(value, min, max, nutrientName) {
    console.log('=== getBarColor called ===');
    console.log('Input parameters:', { value, min, max, nutrientName });
    
    // Try to load tolerance settings from localStorage
    let tolerances = {};
    const localStorageSettings = localStorage.getItem('nutrientToleranceSettings');
    if (localStorageSettings) {
        try {
            tolerances = JSON.parse(localStorageSettings);
            console.log('Loaded tolerances from localStorage:', tolerances);
        } catch (e) {
            console.error('Error parsing localStorage settings:', e);
        }
    }
    
    // Default tolerances if none found
    const defaultTolerances = {
        'N': { below: 0.20, above: 0.30 },
        'P': { below: 0.25, above: 0.25 },
        'K': { below: 0.20, above: 0.35 },
        'Ca': { below: 0.15, above: 0.35 },
        'Mg': { below: 0.25, above: 0.35 },
        'S': { below: 0.25, above: 0.25 },
        'Na': { below: 0.30, above: 0.20 },
        'Fe': { below: 0.20, above: 0.30 },
        'Mn': { below: 0.20, above: 0.30 },
        'Zn': { below: 0.25, above: 0.25 },
        'Cu': { below: 0.25, above: 0.25 },
        'B': { below: 0.20, above: 0.30 },
        'Mo': { below: 0.30, above: 0.20 },
        'Si': { below: 0.25, above: 0.25 },
        'Co': { below: 0.25, above: 0.25 }
    };
    
    // Get tolerance for this nutrient, use saved settings or defaults
    const tolerance = tolerances[nutrientName] || defaultTolerances[nutrientName] || { below: 0.25, above: 0.25 };
    console.log('Using tolerance for', nutrientName, ':', tolerance);
    
    // Apply tolerance to Django-provided ideal ranges
    // This keeps the original ideal ranges intact but adjusts color thresholds
    const lower = min * (1 - tolerance.below);
    const upper = max * (1 + tolerance.above);
    
    console.log(`Color calculation for ${nutrientName}:`);
    console.log(`  Django ideal range: ${min} - ${max}`);
    console.log(`  Tolerance: ${tolerance.below * 100}% below, ${tolerance.above * 100}% above`);
    console.log(`  Color thresholds: ${lower.toFixed(3)} - ${upper.toFixed(3)}`);
    console.log(`  Current value: ${value}`);
    
    if (value >= lower && value <= upper) {
        console.log(`Result: GREEN (acceptable)`);
        return "#339966"; // green
    } else {
        console.log(`Result: RED (outside range)`);
        return "#ff0000"; // red
    }
}

/**
 * Extract numbers from string
 */
function extractAndJoinNumbers(str) {
    let numbers = str.match(/[\d.]+/g);
    return numbers ? parseFloat(numbers.join('')) : NaN;
}

/**
 * Calculate progress bar width and class based on value and ranges
 */
function calculateProgress(value, min, max, deficient_threshold, excessive_threshold) {
    let barWidth, percentage;
    const multiplier = 3;
    
    if (value === 0) {
        return {
            'barWidth': 33.33 / 100 * multiplier,
            'className': 'deficient'
        };
    }
    
    const deficient = min || value * 0.8;
    const excessive = max || value * 1.8;
    const deficient_lower = deficient_threshold || deficient * 0.65;
    const excessive_upper = excessive_threshold || excessive * 1.35;
    
    if (value < deficient * 0.8) {
        percentage = value / deficient * (33.33 / 100) * multiplier;
        return {
            'barWidth': Math.min(percentage, 100),
            'className': 'deficient'
        };
    }
    
    if (value < deficient) {
        percentage = value / deficient * (33.33 / 100) * multiplier;
        return {
            'barWidth': Math.min(percentage, 100),
            'className': 'partial-deficient'
        };
    }
    
    if (value <= excessive) {
        percentage = 33.33 / 100 * multiplier + (value - deficient) / (excessive - deficient) * (33.33 / 100) * multiplier;
        return {
            'barWidth': Math.min(percentage, 100),
            'className': 'acceptable'
        };
    }
    
    if (value <= excessive * 1.8) {
        let percentage = Math.sqrt((value - excessive) / (excessive_upper - excessive));
        percentage = 66.66 / 100 * multiplier + percentage * (33.33 / 100);
        return {
            'barWidth': Math.min(percentage, 100),
            'className': 'partial-excessive'
        };
    }
    
    let percentage = Math.sqrt((value - excessive) / (excessive_upper - excessive));
    percentage = 66.66 / 100 * multiplier + percentage * (33.33 / 100);
    return {
        'barWidth': Math.min(percentage, 100),
        'className': 'excessive'
    };
}

/**
 * Create table row with tolerance-based color logic
 */
function createRow(format, category = '', parenthetical = '', your_level = '', ideal_level_min = '', ideal_level_max = '', deficient = '', excessive = '', metric = '', row_index, n_rows, table_category = '') {
    let rowHtml = '';
    
    if (format === 'rowFormat3Col1Empty4th') {
        let value = extractAndJoinNumbers(your_level);
        let max = extractAndJoinNumbers(ideal_level_max);
        let min = extractAndJoinNumbers(ideal_level_min);
        let excessive_threshold = extractAndJoinNumbers(excessive) || max * 1.15;
        let deficient_threshold = extractAndJoinNumbers(deficient) || min * 0.75;
        
        let barColor = '';
        let { barWidth, className } = calculateProgress(
            value = String(your_level).includes('<') ? 0 : value,
            lower = min,
            upper = max,
            deficient = deficient_threshold,
            excessive = excessive_threshold
        );
        
        // Determine color based on className
        switch (className) {
            case 'deficient':
                barColor = '#ff0000';
                break;
            case 'partial-deficient':
                barColor = '#ff6600';
                break;
            case 'acceptable':
                barColor = '#339966';
                break;
            case 'partial-excessive':
                barColor = '#339966';
                break;
            case 'excessive':
                barColor = '#0000FF';
                break;
            default:
                barColor = '#339966';
        }
        
        // Handle special cases
        if (value === 0 || String(your_level).includes('<')) {
            barWidth = 0;
            barColor = '';
        }
        
        barWidth = barWidth < 0.1 ? '0.1' : barWidth;
        
        let rangeText = '';
        if (min === 0 && max === 0) {
            rangeText = 'N/A';
            barWidth = 0;
        } else {
            rangeText = 'Range: ' + (ideal_level_min !== '' ? ideal_level_min + ' - ' : '') + ' ' + ideal_level_max + ' ' + metric + '</span></span>';
        }
        
        // Apply tolerance-based color logic
        if (!isNaN(value) && !isNaN(min) && !isNaN(max)) {
            // Extract nutrient name from category or parenthetical
            let nutrientName = category || parenthetical || 'Unknown';
            nutrientName = nutrientName.replace(/\([^)]*\)/g, '').trim(); // Remove parentheses
            nutrientName = nutrientName.split(' ')[0]; // Get first word (element name)
            
            // Get color based on tolerance settings
            const toleranceColor = getBarColor(value, min, max, nutrientName);
            barColor = toleranceColor;
        }
        
        rowHtml = '<tr id="' + table_category + row_index + '">' +
            '<td style="vertical-align: middle; text-align: center;">' + parenthetical + '</td>' +
            '<td style="vertical-align: middle; text-align: center;"><span style="display: inline-flex; justify-content: flex-end; gap: 20px; padding-right: 10px;"><span style="width: 70%; text-align: right;">' + (String(your_level).includes('<') ? your_level : value.toFixed(2)) + '</span> <span style="width: 20%">' + metric + '</span></span>' +
            '<td class="fw-light">' +
            '<span class="td-bar">' +
            '<span style="display: inline-flex; justify-content: flex-end; gap: 20px; padding-right: 20px; width: 100%"><span style="width: 50%; text-align: right;">' + rangeText + '</span>' +
            '<span style="width: 50%; text-align: left;">' + (ideal_level_max !== '' ? '' + (barWidth == '0.1' ? '<span style="width: 0.1">' + barWidth + '</span>' : '<span class="bar" style="background: ' + barColor + '; height: 15px; width:calc(' + barWidth + '* 104%);"></span>') : '') + '</span>' +
            '</span>' +
            '</td>' +
            (row_index != n_rows - 1 ? 
                '\n                    <td style="border:0.001px solid transparent; border-right: 2px solid #000"></td>\n                    <td style="border:0.001px solid transparent; border-right: 2px solid #000"></td>\n                    <td style="border:0.001px solid transparent; border-right: 2px solid #000"></td>\n                    ' : 
                '\n                    <td style="border:0.001px solid transparent; border-bottom: 2px solid #000; border-right: 2px solid #000"></td>\n                    <td style="border:0.001px solid transparent; border-bottom: 2px solid #000; border-right: 2px solid #000"></td>\n                    <td style="border:0.001px solid transparent; border-bottom: 2px solid #000; border-right: 2px solid #000"></td>\n                    ') +
            '</tr>';
    }
    
    return rowHtml;
}

// Export functions for use in other scripts
window.plantTherapy = {
    getBarColor,
    createRow,
    calculateProgress,
    extractAndJoinNumbers
}; 