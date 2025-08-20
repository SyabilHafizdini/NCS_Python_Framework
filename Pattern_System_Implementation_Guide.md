# Pattern System Implementation Guide

## Overview

The Pattern System is a dynamic locator generation framework for test automation that allows test scripts to use semantic field names instead of hardcoded XPath locators. The system automatically resolves element locators at runtime using predefined patterns, making tests more maintainable and readable.

## Architecture Components

### 1. Test Step Layer (web.java)
**Location**: `src/test/java/com/ahq/globals/web.java:1047`

The entry point for pattern-based interactions. Example method:

```java
@QAFTestStep(description = "Web: Click-Element Pattern:{pattern_name} Field:{field_link_name}")
@And("Web: Click-Element Pattern:{string} Field:{string}")
public static void clickElement_Web(String pattern_name, String field_link_name) throws Exception {
    Class<?> patternLocClass = patternLoc.class;
    try {
        // Use reflection to dynamically call pattern method
        Method method = patternLocClass.getMethod(pattern_name, String.class, String.class);
        Reporter.log("Found function " + pattern_name + " in patternLoc.java!");
        
        // Invoke method with current page and field name
        Object result = method.invoke(null, getPageName(), field_link_name);
        
        // Perform browser action with resolved locator
        BrowserGlobal.iClickOn(waitForFieldToBePresentScrollToCenterViewAndEnabled((String) result));
    } catch (NoSuchMethodException e) {
        throw new Exception("No such method: " + pattern_name + " in patternLoc", e);
    } catch (Exception e) {
        throw new Exception("Error invoking method: " + pattern_name, e);
    }
}
```

**Key Features:**
- Uses reflection for dynamic method resolution
- Handles exceptions gracefully
- Integrates with existing browser automation framework

### 2. Pattern Resolution Engine (patternLoc.java)
**Location**: `src/test/java/com/ahq/addons/patternLoc.java`

Contains individual methods for each element type following a consistent pattern:

```java
public static String button(String page, String fieldName) throws Exception {
    String fieldType = "button";
    String locator = checkLoc(page, fieldType, fieldName);
    if (locator.contains("auto.")) {
        generateLoc(locator, fieldName, fieldType);
    }
    return locator;
}
```

#### Core Methods

**checkLoc() - Line 499**
```java
public static String checkLoc(String argPageName, String argFieldType, String argFieldName) {
    // Clear auto-generation variables
    getBundle().setProperty("loc.auto.fieldName", "");
    getBundle().setProperty("loc.auto.fieldInstance", "");
    getBundle().setProperty("loc.auto.forValue", "");
    getBundle().setProperty("loc.auto.fieldValue", "");

    String patternCode = getPatternCode();
    
    // Generate camelCase locator name
    String locName = patternCode + "." + 
        CaseUtils.toCamelCase(argPageName.replaceAll("[^a-zA-Z0-9]", " "), false, ' ') + "." +
        CaseUtils.toCamelCase(argFieldType.replaceAll("d365_", "").replaceAll("[^a-zA-Z0-9]", " "), false, ' ').trim() + "." +
        CaseUtils.toCamelCase(argFieldName.replaceAll("[^a-zA-Z0-9]", " "), false, ' ').trim();
    
    String locVal = getBundle().getPropertyValue(locName);
    
    // If no explicit locator found, mark for auto-generation
    if (locVal.equals(locName) || locVal.length() < 5) {
        locName = "auto." + locName;
    }
    return locName;
}
```

**generateLoc() - Line 515**
```java
public static void generateLoc(String argLocator, String argFieldName, String argFieldType) {
    String patternCodeVal = getPatternCode();
    
    // Set field variables for pattern substitution
    getBundle().setProperty("loc.auto.fieldName", fieldNameCheck(argFieldName));
    getBundle().setProperty("loc.auto.fieldInstance", fieldInstanceCheck(argFieldName));
    
    // Get pattern template
    String locPattern = patternCodeVal + ".pattern." + argFieldType;
    String locPatternVal = getBundle().getPropertyValue(locPattern);
    
    if (locPatternVal.equals(locPattern) || locPatternVal.length() < 5) {
        System.out.println("=====>[ERROR] => [Locator Pattern '" + locPattern + "' not available]");
    } else {
        // Generate final locator with JSON format
        getBundle().setProperty(argLocator, 
            "{\"locator\":[" + locPatternVal + "],\"desc\":\"" + argFieldName + " : [" + argFieldType + "] Field \"}");
    }
}
```

**Helper Methods:**
- `fieldNameCheck()` - Extracts field name from bracketed instances like "Submit[2]"
- `fieldInstanceCheck()` - Extracts instance number, returns "1" if not specified
- `getPatternCode()` - Gets the pattern code prefix from configuration

#### Supported Element Types

The system supports 50+ element types including:
- `button` - Buttons and clickable elements
- `input` - Text fields and form inputs  
- `link` - Hyperlinks and navigation elements
- `checkbox` - Checkboxes and toggle elements
- `dropdown` - Select dropdowns and option lists
- `text` - Text elements and labels
- `header` - Page headers and titles
- `card` - Card components
- `tab` - Tab navigation elements
- `table` - Table elements and data grids

### 3. Pattern Configuration (locPattern.properties)
**Location**: `resources/locators/locPattern.properties`

Defines XPath templates with placeholder variables for dynamic substitution:

```properties
# Button patterns with multiple fallback options
loc.spfNgen.pattern.button="xpath=//BUTTON//span[text()='${loc.auto.fieldName}']", \
  "xpath=//BUTTON[text()='${loc.auto.fieldName}']", \
  "xpath=//input[@value='${loc.auto.fieldName}']", \
  "xpath=//button[@aria-label='${loc.auto.fieldName}']"

# Input field patterns
loc.spfNgen.pattern.input="xpath=//INPUT[@id='${loc.auto.forValue}']", \
  "xpath=//INPUT[@placeholder='${loc.auto.fieldName}']", \
  "xpath=//textarea[@id='${loc.auto.forValue}']", \
  "id=${loc.auto.forValue}"

# Link patterns  
loc.spfNgen.pattern.link="xpath=//A//DIV[text()='${loc.auto.fieldName}']", \
  "xpath=//A//SPAN[text()='${loc.auto.fieldName}']", \
  "xpath=//a[text()='${loc.auto.fieldName}']"

# Card pattern for application selection
loc.spfNgen.pattern.card="xpath=//span[text()='Published Apps']/ancestor::div[@class='app-list-container']//div[@data-type='app-title'][@title='${loc.auto.fieldName}']"
```

#### Available Variables

- `${loc.auto.fieldName}` - The field name passed from test step
- `${loc.auto.forValue}` - Label's "for" attribute value for form association
- `${loc.auto.fieldValue}` - Values for radio buttons and checkboxes
- `${loc.auto.fieldInstance}` - Instance number for duplicate field names

## Implementation Workflow

### Example: Test Step Execution

**Test Step**: `Then Web: Click-Element Pattern:"button" Field:"Next"`

1. **Entry Point** - `clickElement_Web("button", "Next")` called
2. **Reflection** - Dynamically calls `patternLoc.button("currentPage", "Next")`
3. **Locator Check** - Looks for explicit locator: `loc.spfNgen.currentPage.button.next`
4. **Auto-Generation** - If not found, uses pattern: `loc.spfNgen.pattern.button`
5. **Variable Substitution** - Replaces `${loc.auto.fieldName}` with "Next"
6. **Fallback Resolution** - Tries each XPath option until element found
7. **Final Locator** - Returns: `xpath=//BUTTON//span[text()='Next']`
8. **Execution** - Performs click action on resolved element

### Instance Handling

For duplicate field names, use bracket notation:
```gherkin
Then Web: Click-Element Pattern:"button" Field:"Submit[2]"
```

This resolves to the second "Submit" button on the page.

## Implementation Guide for AI Systems

### Step 1: Core Infrastructure

```java
public class PatternLocatorEngine {
    
    // Element type methods (one per supported element)
    public static String button(String page, String fieldName) throws Exception {
        return resolvePattern("button", page, fieldName);
    }
    
    public static String input(String page, String fieldName) throws Exception {
        return resolvePattern("input", page, fieldName);
    }
    
    // Add methods for each element type...
    
    private static String resolvePattern(String elementType, String page, String fieldName) throws Exception {
        // 1. Generate property key using camelCase conversion
        String propertyKey = generatePropertyKey(patternCode, page, elementType, fieldName);
        
        // 2. Check for explicit locator definition
        String explicitLocator = getProperty(propertyKey);
        if (explicitLocator != null && !explicitLocator.isEmpty()) {
            return explicitLocator;
        }
        
        // 3. Use pattern-based generation
        return generateFromPattern(elementType, fieldName);
    }
    
    private static String generateFromPattern(String elementType, String fieldName) throws Exception {
        // 1. Get pattern template from properties
        String patternKey = patternCode + ".pattern." + elementType;
        String patternTemplate = getProperty(patternKey);
        
        // 2. Set up variable substitutions
        setVariable("loc.auto.fieldName", extractFieldName(fieldName));
        setVariable("loc.auto.fieldInstance", extractInstance(fieldName));
        
        // 3. Perform variable substitution in template
        String resolvedPattern = substituteVariables(patternTemplate);
        
        // 4. Return in QAF JSON format
        return "{\"locator\":[" + resolvedPattern + "],\"desc\":\"" + fieldName + " : [" + elementType + "] Field \"}";
    }
}
```

### Step 2: Test Framework Integration

```java
public class WebActions {
    
    @TestStep("Web: Click-Element Pattern:{elementType} Field:{fieldName}")
    public void clickElement(String elementType, String fieldName) throws Exception {
        try {
            // Use reflection to call appropriate pattern method
            Method patternMethod = PatternLocatorEngine.class.getMethod(elementType, String.class, String.class);
            String locator = (String) patternMethod.invoke(null, getCurrentPage(), fieldName);
            
            // Perform browser action
            browserDriver.click(locator);
            
        } catch (NoSuchMethodException e) {
            throw new TestException("Unsupported element type: " + elementType);
        } catch (Exception e) {
            throw new TestException("Failed to click element: " + fieldName, e);
        }
    }
    
    // Implement similar methods for other actions...
}
```

### Step 3: Configuration Management

```properties
# Pattern configuration file
pattern.code=myApp

# Element patterns with fallback options
myApp.pattern.button="xpath=//button[text()='${loc.auto.fieldName}']", \
                     "xpath=//input[@value='${loc.auto.fieldName}']", \
                     "xpath=//button[@aria-label='${loc.auto.fieldName}']"

myApp.pattern.input="xpath=//input[@placeholder='${loc.auto.fieldName}']", \
                    "xpath=//input[@id='${loc.auto.forValue}']", \
                    "id=${loc.auto.forValue}"

# Page-specific overrides
myApp.loginPage.button.submit="xpath=//form[@id='login']//button[@type='submit']"
```

### Step 4: Advanced Features

#### Label Association for Form Fields

```java
private static void establishLabelAssociation(String fieldName) throws Exception {
    // Find label element
    String labelPattern = patternCode + ".pattern.label";
    String labelLocator = substituteVariables(getProperty(labelPattern));
    
    if (isElementPresent(labelLocator)) {
        // Extract 'for' attribute value
        String forValue = getAttribute(labelLocator, "for");
        setVariable("loc.auto.forValue", forValue);
    }
}
```

#### Multi-Pattern Fallback System

```java
private static String tryMultiplePatterns(String patternTemplate) throws Exception {
    String[] patterns = parsePatternArray(patternTemplate);
    
    for (String pattern : patterns) {
        String resolvedPattern = substituteVariables(pattern);
        if (isElementPresent(resolvedPattern)) {
            return resolvedPattern;
        }
    }
    
    throw new ElementNotFoundException("No matching pattern found");
}
```

## Best Practices

### 1. Pattern Design
- Use multiple fallback options for robustness
- Order patterns from most specific to most generic
- Include accessibility attributes (aria-label, role)
- Consider different HTML structures for same logical element

### 2. Naming Conventions
- Use descriptive field names matching UI labels
- Employ camelCase for property keys
- Prefix with pattern code for namespacing
- Use consistent element type names

### 3. Maintenance
- Group related patterns by application area
- Document pattern variables and their usage
- Implement pattern validation and testing
- Version control pattern configurations

### 4. Error Handling
- Provide clear error messages for missing patterns
- Log pattern resolution steps for debugging
- Implement graceful fallbacks for edge cases
- Validate pattern syntax before execution

## Benefits

1. **Maintainability** - UI changes require only pattern updates, not test script changes
2. **Readability** - Tests use business terminology instead of technical locators  
3. **Reusability** - Patterns can be shared across multiple test suites
4. **Scalability** - New element types can be added without changing existing tests
5. **Flexibility** - Multiple locator strategies provide robust element finding
6. **Documentation** - Self-documenting tests through semantic field names

## Migration Strategy

1. **Assessment** - Identify existing hardcoded locators in test suite
2. **Pattern Creation** - Develop patterns for common element types
3. **Gradual Migration** - Convert tests incrementally by feature area
4. **Validation** - Ensure converted tests maintain same functionality
5. **Training** - Educate team on pattern system usage and maintenance

This pattern system transforms brittle, maintenance-heavy test automation into a robust, scalable solution that adapts to application changes while maintaining test readability and business relevance.