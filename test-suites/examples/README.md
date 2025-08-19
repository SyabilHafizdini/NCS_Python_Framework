# Test Suite Examples

This directory contains example XML configuration files demonstrating different types of test suites and configurations for the QAF-Python Test Suite Management feature.

## Available Examples

### 1. `basic-smoke.xml`
**Purpose:** Simple smoke test suite for quick validation  
**Features:**
- Basic parameter configuration
- Simple tag filtering (include smoke, exclude manual)
- Minimal execution requirements
- Perfect for daily builds or quick health checks

**Use Case:** Start here if you're new to test suites or need a simple validation suite.

---

### 2. `smoke-suite.xml`
**Purpose:** Enhanced smoke test suite with more comprehensive coverage  
**Features:**
- Environment-specific configuration (UAT)
- Multiple include tags (smoke, critical)
- Specific feature file targeting
- Basic timeout configuration

**Use Case:** More robust smoke testing with environment awareness.

---

### 3. `regression-suite.xml`
**Purpose:** Comprehensive regression testing with advanced configuration  
**Features:**
- Advanced execution configuration with timeouts and retries
- Environment profiles and variable management
- Extensive test coverage across multiple modules
- Error handling and recovery options

**Use Case:** Weekly or release regression testing with comprehensive coverage.

---

### 4. `advanced-suite.xml`
**Purpose:** Demonstration of all advanced features  
**Features:**
- Complex execution configuration
- Multiple environment profiles with inheritance
- Advanced retry and timeout strategies
- Comprehensive parameter management

**Use Case:** Reference for implementing complex testing scenarios.

---

### 5. `api-validation.xml` (New)
**Purpose:** API-focused testing suite  
**Features:**
- API-specific parameters (base_url, version, authentication)
- Optimized timeouts for API calls
- Database and cache management for isolated testing
- API-focused tag filtering

**Use Case:** Backend/API validation, integration testing, microservices testing.

---

### 6. `mobile-tests.xml` (New)
**Purpose:** Mobile application testing  
**Features:**
- Mobile platform configuration (Android/iOS)
- Device-specific parameters
- Mobile-optimized timeouts and retry logic
- Screenshot and video recording for mobile debugging

**Use Case:** Mobile app testing, responsive design validation, mobile-specific workflows.

---

### 7. `ci-pipeline.xml` (New)
**Purpose:** CI/CD pipeline optimized suite  
**Features:**
- Fast execution with minimal timeouts
- Headless browser configuration
- CI-specific environment variables
- Optimized for automated build systems

**Use Case:** Continuous integration, automated deployments, build verification.

---

### 8. `cross-browser.xml` (New)
**Purpose:** Cross-browser compatibility testing  
**Features:**
- Browser matrix configuration
- Visual testing and screenshot comparison
- Performance and accessibility checks
- UI-focused test filtering

**Use Case:** Cross-browser compatibility, visual regression testing, accessibility validation.

## How to Use These Examples

### 1. Copy and Customize
```bash
cp test-suites/examples/basic-smoke.xml test-suites/my-custom-suite.xml
# Edit my-custom-suite.xml to match your needs
```

### 2. Execute Examples
```bash
python run_tests.py --suite-config test-suites/examples/basic-smoke.xml
```

### 3. Validate Examples
```bash
python run_tests.py --validate-suite test-suites/examples/basic-smoke.xml
```

### 4. Preview Commands
```bash
python run_tests.py --suite-config test-suites/examples/regression-suite.xml --dry-run
```

## Customization Guide

### Common Modifications

1. **Update Base URL:**
   ```xml
   <parameter name="base_url" value="https://your-app.com"/>
   ```

2. **Change Browser:**
   ```xml
   <parameter name="browser" value="firefox"/>
   ```

3. **Modify Tags:**
   ```xml
   <include name="your-tag"/>
   <exclude name="skip-tag"/>
   ```

4. **Update Test Paths:**
   ```xml
   <class name="your.tests.module"/>
   ```

### Environment-Specific Suites

Create different versions for different environments:
- `smoke-dev.xml` - Development environment
- `smoke-staging.xml` - Staging environment  
- `smoke-prod.xml` - Production environment

### Tag Strategy Examples

- **By Priority:** `critical`, `high`, `medium`, `low`
- **By Feature:** `login`, `checkout`, `inventory`, `api`
- **By Type:** `smoke`, `regression`, `integration`, `e2e`
- **By Speed:** `fast`, `medium`, `slow`

## Integration Examples

### Jenkins Integration
```groovy
pipeline {
    stages {
        stage('Smoke Tests') {
            steps {
                sh 'python run_tests.py --suite-config test-suites/examples/ci-pipeline.xml'
            }
        }
    }
}
```

### GitHub Actions Integration
```yaml
- name: Run Test Suite
  run: |
    python run_tests.py --suite-config test-suites/examples/api-validation.xml
```

## Best Practices

1. **Start Simple:** Begin with `basic-smoke.xml` and gradually add complexity
2. **Environment Consistency:** Use consistent parameter names across suites
3. **Tag Strategy:** Develop a consistent tagging strategy for your team
4. **Documentation:** Always include descriptive descriptions in your suites
5. **Validation:** Always validate suites before committing to version control

## Troubleshooting

If you encounter issues with any example:

1. **Validate the suite:**
   ```bash
   python run_tests.py --validate-suite test-suites/examples/[suite-name].xml
   ```

2. **Check feature file paths:**
   Ensure the `<class>` paths match your actual feature file structure

3. **Verify tags:**
   Ensure your feature files have the tags referenced in the suite

4. **Test with dry-run:**
   ```bash
   python run_tests.py --suite-config test-suites/examples/[suite-name].xml --dry-run
   ```

## Contributing

When adding new examples:
1. Follow the naming convention: `[purpose]-[type].xml`
2. Include comprehensive comments and descriptions
3. Update this README with the new example
4. Test the example thoroughly before committing

For more detailed information, see the [Test Suite Management Guide](../../docs/TEST_SUITE_MANAGEMENT.md).