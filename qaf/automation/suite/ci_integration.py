#  Copyright (c) 2022 Infostretch Corporation
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  #
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

"""
CI/CD integration support for test suite execution
"""

import os
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

from .exceptions import SuiteEnvironmentError, SuiteExecutionError, handle_exception
from .parser import SuiteConfiguration
from .executor import SuiteExecutor, ExecutionResult


@dataclass
class CIEnvironment:
    """Information about the CI/CD environment"""
    provider: str  # jenkins, github, gitlab, azure, bamboo, etc.
    build_number: Optional[str] = None
    build_url: Optional[str] = None
    branch: Optional[str] = None
    commit_hash: Optional[str] = None
    pull_request: Optional[str] = None
    job_name: Optional[str] = None
    workspace: Optional[str] = None
    node_name: Optional[str] = None
    
    @classmethod
    def detect_environment(cls) -> 'CIEnvironment':
        """Detect CI/CD environment from environment variables"""
        
        # Jenkins
        if os.getenv('JENKINS_URL'):
            return cls(
                provider='jenkins',
                build_number=os.getenv('BUILD_NUMBER'),
                build_url=os.getenv('BUILD_URL'),
                branch=os.getenv('GIT_BRANCH'),
                commit_hash=os.getenv('GIT_COMMIT'),
                job_name=os.getenv('JOB_NAME'),
                workspace=os.getenv('WORKSPACE'),
                node_name=os.getenv('NODE_NAME')
            )
        
        # GitHub Actions
        elif os.getenv('GITHUB_ACTIONS'):
            return cls(
                provider='github',
                build_number=os.getenv('GITHUB_RUN_NUMBER'),
                build_url=f"{os.getenv('GITHUB_SERVER_URL')}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}",
                branch=os.getenv('GITHUB_REF_NAME'),
                commit_hash=os.getenv('GITHUB_SHA'),
                pull_request=os.getenv('GITHUB_PR_NUMBER'),
                job_name=os.getenv('GITHUB_JOB'),
                workspace=os.getenv('GITHUB_WORKSPACE')
            )
        
        # GitLab CI
        elif os.getenv('GITLAB_CI'):
            return cls(
                provider='gitlab',
                build_number=os.getenv('CI_PIPELINE_ID'),
                build_url=os.getenv('CI_PIPELINE_URL'),
                branch=os.getenv('CI_COMMIT_REF_NAME'),
                commit_hash=os.getenv('CI_COMMIT_SHA'),
                pull_request=os.getenv('CI_MERGE_REQUEST_IID'),
                job_name=os.getenv('CI_JOB_NAME'),
                workspace=os.getenv('CI_PROJECT_DIR'),
                node_name=os.getenv('CI_RUNNER_DESCRIPTION')
            )
        
        # Azure DevOps
        elif os.getenv('AZURE_HTTP_USER_AGENT'):
            return cls(
                provider='azure',
                build_number=os.getenv('BUILD_BUILDNUMBER'),
                build_url=f"{os.getenv('SYSTEM_TEAMFOUNDATIONCOLLECTIONURI')}{os.getenv('SYSTEM_TEAMPROJECT')}/_build/results?buildId={os.getenv('BUILD_BUILDID')}",
                branch=os.getenv('BUILD_SOURCEBRANCHNAME'),
                commit_hash=os.getenv('BUILD_SOURCEVERSION'),
                pull_request=os.getenv('SYSTEM_PULLREQUEST_PULLREQUESTNUMBER'),
                job_name=os.getenv('AGENT_JOBNAME'),
                workspace=os.getenv('BUILD_SOURCESDIRECTORY'),
                node_name=os.getenv('AGENT_NAME')
            )
        
        # Bamboo
        elif os.getenv('bamboo_buildKey'):
            return cls(
                provider='bamboo',
                build_number=os.getenv('bamboo_buildNumber'),
                build_url=os.getenv('bamboo_buildResultsUrl'),
                branch=os.getenv('bamboo_planRepository_branchName'),
                commit_hash=os.getenv('bamboo_planRepository_revision'),
                job_name=os.getenv('bamboo_shortJobName'),
                workspace=os.getenv('bamboo_build_working_directory'),
                node_name=os.getenv('bamboo_agentId')
            )
        
        # TeamCity
        elif os.getenv('TEAMCITY_VERSION'):
            return cls(
                provider='teamcity',
                build_number=os.getenv('BUILD_NUMBER'),
                build_url=f"{os.getenv('TEAMCITY_SERVER_URL')}/viewLog.html?buildId={os.getenv('TEAMCITY_BUILD_ID')}",
                branch=os.getenv('TEAMCITY_BUILD_BRANCH'),
                commit_hash=os.getenv('BUILD_VCS_NUMBER'),
                job_name=os.getenv('TEAMCITY_BUILDCONF_NAME'),
                workspace=os.getenv('TEAMCITY_BUILD_CHECKOUTDIR'),
                node_name=os.getenv('AGENT_NAME')
            )
        
        # CircleCI
        elif os.getenv('CIRCLECI'):
            return cls(
                provider='circleci',
                build_number=os.getenv('CIRCLE_BUILD_NUM'),
                build_url=os.getenv('CIRCLE_BUILD_URL'),
                branch=os.getenv('CIRCLE_BRANCH'),
                commit_hash=os.getenv('CIRCLE_SHA1'),
                pull_request=os.getenv('CIRCLE_PR_NUMBER'),
                job_name=os.getenv('CIRCLE_JOB'),
                workspace=os.getenv('CIRCLE_WORKING_DIRECTORY'),
                node_name=os.getenv('CIRCLE_NODE_INDEX')
            )
        
        # Travis CI
        elif os.getenv('TRAVIS'):
            return cls(
                provider='travis',
                build_number=os.getenv('TRAVIS_BUILD_NUMBER'),
                build_url=f"https://travis-ci.org/{os.getenv('TRAVIS_REPO_SLUG')}/builds/{os.getenv('TRAVIS_BUILD_ID')}",
                branch=os.getenv('TRAVIS_BRANCH'),
                commit_hash=os.getenv('TRAVIS_COMMIT'),
                pull_request=os.getenv('TRAVIS_PULL_REQUEST') if os.getenv('TRAVIS_PULL_REQUEST') != 'false' else None,
                job_name=os.getenv('TRAVIS_JOB_NAME'),
                workspace=os.getenv('TRAVIS_BUILD_DIR')
            )
        
        # Generic/Unknown
        else:
            return cls(
                provider='unknown',
                workspace=os.getcwd()
            )


@dataclass
class CIExecutionConfig:
    """Configuration for CI/CD execution"""
    fail_fast: bool = False
    continue_on_error: bool = False
    timeout_minutes: int = 60
    retry_count: int = 0
    retry_delay_seconds: int = 10
    parallel_execution: bool = False
    max_parallel_jobs: int = 1
    environment_variables: Dict[str, str] = None
    output_formats: List[str] = None
    report_artifacts: List[str] = None
    notification_webhooks: List[str] = None
    
    def __post_init__(self):
        if self.environment_variables is None:
            self.environment_variables = {}
        if self.output_formats is None:
            self.output_formats = ['allure', 'junit']
        if self.report_artifacts is None:
            self.report_artifacts = ['reports/allure-results', 'reports/test_reports']
        if self.notification_webhooks is None:
            self.notification_webhooks = []


@dataclass
class CIExecutionResult:
    """Result of CI/CD execution"""
    success: bool
    exit_code: int
    duration_seconds: float
    execution_result: ExecutionResult
    ci_environment: CIEnvironment
    artifacts_generated: List[str]
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_json(self) -> str:
        """Convert result to JSON for CI/CD consumption"""
        return json.dumps(asdict(self), indent=2, default=str)
    
    def to_junit_xml(self) -> str:
        """Convert result to JUnit XML format"""
        root = ET.Element('testsuites')
        root.set('name', 'QAF Suite Execution')
        root.set('tests', str(self.execution_result.passed + self.execution_result.failed))
        root.set('failures', str(self.execution_result.failed))
        root.set('time', str(self.duration_seconds))
        
        testsuite = ET.SubElement(root, 'testsuite')
        testsuite.set('name', 'Suite Execution')
        testsuite.set('tests', str(self.execution_result.passed + self.execution_result.failed))
        testsuite.set('failures', str(self.execution_result.failed))
        testsuite.set('time', str(self.duration_seconds))
        
        # Add test case for overall execution
        testcase = ET.SubElement(testsuite, 'testcase')
        testcase.set('classname', 'QAF.SuiteExecution')
        testcase.set('name', 'ExecuteSuite')
        testcase.set('time', str(self.duration_seconds))
        
        if not self.success:
            failure = ET.SubElement(testcase, 'failure')
            failure.set('message', self.error_message or 'Suite execution failed')
            failure.text = f"Exit code: {self.exit_code}"
        
        return ET.tostring(root, encoding='unicode')


class CIIntegrator:
    """
    CI/CD integration manager for test suite execution
    """
    
    def __init__(self, executor: Optional[SuiteExecutor] = None):
        """
        Initialize CI integrator
        
        Args:
            executor: Suite executor instance (creates default if None)
        """
        self.executor = executor or SuiteExecutor()
        self.ci_environment = CIEnvironment.detect_environment()
    
    @handle_exception
    def execute_suite_for_ci(self, 
                           config: SuiteConfiguration, 
                           ci_config: CIExecutionConfig = None) -> CIExecutionResult:
        """
        Execute test suite with CI/CD specific configuration
        
        Args:
            config: Suite configuration
            ci_config: CI execution configuration
            
        Returns:
            CIExecutionResult with execution details
        """
        if ci_config is None:
            ci_config = CIExecutionConfig()
        
        # Apply CI environment variables to suite config
        self._apply_ci_environment_variables(config, ci_config)
        
        # Setup execution environment
        self._setup_execution_environment(ci_config)
        
        start_time = self._get_current_time()
        artifacts_generated = []
        error_message = None
        retry_count = 0
        
        try:
            # Execute with retries if configured
            execution_result = self._execute_with_retries(config, ci_config, retry_count)
            
            # Generate artifacts
            artifacts_generated = self._generate_ci_artifacts(execution_result, ci_config)
            
            # Determine success based on exit code and configuration
            success = self._determine_success(execution_result, ci_config)
            
            end_time = self._get_current_time()
            duration = end_time - start_time
            
            result = CIExecutionResult(
                success=success,
                exit_code=execution_result.exit_code,
                duration_seconds=duration,
                execution_result=execution_result,
                ci_environment=self.ci_environment,
                artifacts_generated=artifacts_generated,
                error_message=error_message,
                retry_count=retry_count
            )
            
            # Send notifications if configured
            self._send_notifications(result, ci_config)
            
            return result
            
        except Exception as e:
            end_time = self._get_current_time()
            duration = end_time - start_time
            error_message = str(e)
            
            # Create failed result
            failed_result = ExecutionResult(
                suite_name=config.name,
                exit_code=1,
                execution_time=duration,
                passed=0,
                failed=0,
                skipped=0,
                command_executed="Execution failed due to exception"
            )
            
            result = CIExecutionResult(
                success=False,
                exit_code=1,
                duration_seconds=duration,
                execution_result=failed_result,
                ci_environment=self.ci_environment,
                artifacts_generated=artifacts_generated,
                error_message=error_message,
                retry_count=retry_count
            )
            
            if not ci_config.continue_on_error:
                raise SuiteExecutionError(f"CI execution failed: {error_message}")
            
            return result
    
    def _apply_ci_environment_variables(self, config: SuiteConfiguration, ci_config: CIExecutionConfig):
        """Apply CI environment variables to suite configuration"""
        if not config.environment_params:
            config.environment_params = {}
        
        # Add CI-specific environment variables
        ci_vars = {
            'CI_PROVIDER': self.ci_environment.provider,
            'CI_BUILD_NUMBER': self.ci_environment.build_number or '',
            'CI_BUILD_URL': self.ci_environment.build_url or '',
            'CI_BRANCH': self.ci_environment.branch or '',
            'CI_COMMIT_HASH': self.ci_environment.commit_hash or '',
            'CI_JOB_NAME': self.ci_environment.job_name or '',
            'CI_WORKSPACE': self.ci_environment.workspace or ''
        }
        
        # Add custom environment variables
        ci_vars.update(ci_config.environment_variables)
        
        # Apply to configuration (don't override existing)
        for key, value in ci_vars.items():
            if key not in config.environment_params:
                config.environment_params[key] = value
    
    def _setup_execution_environment(self, ci_config: CIExecutionConfig):
        """Setup execution environment for CI/CD"""
        # Set environment variables
        for key, value in ci_config.environment_variables.items():
            os.environ[key] = value
        
        # Ensure report directories exist
        for artifact_path in ci_config.report_artifacts:
            Path(artifact_path).mkdir(parents=True, exist_ok=True)
    
    def _execute_with_retries(self, config: SuiteConfiguration, ci_config: CIExecutionConfig, retry_count: int) -> ExecutionResult:
        """Execute suite with retry logic"""
        last_exception = None
        
        for attempt in range(ci_config.retry_count + 1):
            try:
                result = self.executor.execute_suite(config)
                
                # Check if we should retry based on result
                if result.exit_code == 0 or not ci_config.retry_count:
                    return result
                
                # If this is not the last attempt and we have failures, retry
                if attempt < ci_config.retry_count:
                    import time
                    time.sleep(ci_config.retry_delay_seconds)
                    retry_count += 1
                    continue
                
                return result
                
            except Exception as e:
                last_exception = e
                if attempt < ci_config.retry_count:
                    import time
                    time.sleep(ci_config.retry_delay_seconds)
                    retry_count += 1
                    continue
                raise
        
        if last_exception:
            raise last_exception
    
    def _determine_success(self, result: ExecutionResult, ci_config: CIExecutionConfig) -> bool:
        """Determine if execution was successful based on configuration"""
        if ci_config.fail_fast and result.failed > 0:
            return False
        
        if ci_config.continue_on_error:
            return True
        
        return result.exit_code == 0
    
    def _generate_ci_artifacts(self, result: ExecutionResult, ci_config: CIExecutionConfig) -> List[str]:
        """Generate CI/CD artifacts"""
        artifacts = []
        
        try:
            # Generate JUnit XML if requested
            if 'junit' in ci_config.output_formats:
                junit_path = 'reports/junit-results.xml'
                ci_result = CIExecutionResult(
                    success=result.exit_code == 0,
                    exit_code=result.exit_code,
                    duration_seconds=result.execution_time,
                    execution_result=result,
                    ci_environment=self.ci_environment,
                    artifacts_generated=[]
                )
                
                Path(junit_path).parent.mkdir(parents=True, exist_ok=True)
                with open(junit_path, 'w') as f:
                    f.write(ci_result.to_junit_xml())
                artifacts.append(junit_path)
            
            # Generate JSON report if requested
            if 'json' in ci_config.output_formats:
                json_path = 'reports/execution-result.json'
                ci_result = CIExecutionResult(
                    success=result.exit_code == 0,
                    exit_code=result.exit_code,
                    duration_seconds=result.execution_time,
                    execution_result=result,
                    ci_environment=self.ci_environment,
                    artifacts_generated=[]
                )
                
                Path(json_path).parent.mkdir(parents=True, exist_ok=True)
                with open(json_path, 'w') as f:
                    f.write(ci_result.to_json())
                artifacts.append(json_path)
            
            # Copy existing artifacts
            for artifact_path in ci_config.report_artifacts:
                if os.path.exists(artifact_path):
                    artifacts.append(artifact_path)
        
        except Exception as e:
            # Don't fail execution due to artifact generation issues
            print(f"Warning: Failed to generate some artifacts: {e}")
        
        return artifacts
    
    def _send_notifications(self, result: CIExecutionResult, ci_config: CIExecutionConfig):
        """Send notifications to configured webhooks"""
        if not ci_config.notification_webhooks:
            return
        
        notification_data = {
            'success': result.success,
            'exit_code': result.exit_code,
            'duration': result.duration_seconds,
            'scenarios_passed': result.execution_result.passed,
            'scenarios_failed': result.execution_result.failed,
            'ci_provider': result.ci_environment.provider,
            'build_number': result.ci_environment.build_number,
            'build_url': result.ci_environment.build_url,
            'branch': result.ci_environment.branch,
            'commit_hash': result.ci_environment.commit_hash
        }
        
        for webhook_url in ci_config.notification_webhooks:
            try:
                import requests
                requests.post(webhook_url, json=notification_data, timeout=10)
            except Exception as e:
                print(f"Warning: Failed to send notification to {webhook_url}: {e}")
    
    def _get_current_time(self) -> float:
        """Get current time in seconds"""
        import time
        return time.time()
    
    def get_ci_environment_info(self) -> Dict[str, Any]:
        """Get comprehensive CI environment information"""
        return {
            'detected_provider': self.ci_environment.provider,
            'environment_details': asdict(self.ci_environment),
            'available_variables': self._get_available_ci_variables(),
            'recommendations': self._get_ci_recommendations()
        }
    
    def _get_available_ci_variables(self) -> Dict[str, str]:
        """Get available CI environment variables"""
        ci_vars = {}
        ci_prefixes = ['CI_', 'BUILD_', 'GITHUB_', 'GITLAB_', 'JENKINS_', 'TEAMCITY_', 'BAMBOO_', 'TRAVIS_', 'CIRCLE_']
        
        for key, value in os.environ.items():
            if any(key.startswith(prefix) for prefix in ci_prefixes):
                ci_vars[key] = value
        
        return ci_vars
    
    def _get_ci_recommendations(self) -> List[str]:
        """Get CI/CD integration recommendations"""
        recommendations = []
        
        if self.ci_environment.provider == 'unknown':
            recommendations.append("Consider setting standard CI environment variables for better integration")
        
        if not os.path.exists('reports'):
            recommendations.append("Create 'reports' directory for artifact storage")
        
        if not os.path.exists('behave.ini'):
            recommendations.append("Configure behave.ini for consistent test execution")
        
        recommendations.append("Configure artifact collection for test reports")
        recommendations.append("Set up failure notifications for critical test failures")
        
        return recommendations


def get_ci_exit_code(execution_result: ExecutionResult, fail_fast: bool = False) -> int:
    """
    Get appropriate exit code for CI/CD systems
    
    Args:
        execution_result: Suite execution result
        fail_fast: Whether to fail immediately on any test failure
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    if execution_result.exit_code != 0:
        return execution_result.exit_code
    
    if fail_fast and execution_result.failed > 0:
        return 1
    
    # Success if no system-level failures
    return 0


def create_ci_config_from_env() -> CIExecutionConfig:
    """
    Create CI execution configuration from environment variables
    
    Returns:
        CIExecutionConfig populated from environment variables
    """
    return CIExecutionConfig(
        fail_fast=os.getenv('QAF_FAIL_FAST', 'false').lower() == 'true',
        continue_on_error=os.getenv('QAF_CONTINUE_ON_ERROR', 'false').lower() == 'true',
        timeout_minutes=int(os.getenv('QAF_TIMEOUT_MINUTES', '60')),
        retry_count=int(os.getenv('QAF_RETRY_COUNT', '0')),
        retry_delay_seconds=int(os.getenv('QAF_RETRY_DELAY', '10')),
        parallel_execution=os.getenv('QAF_PARALLEL', 'false').lower() == 'true',
        max_parallel_jobs=int(os.getenv('QAF_PARALLEL_JOBS', '1')),
        environment_variables={
            key[4:]: value for key, value in os.environ.items() 
            if key.startswith('QAF_') and key not in [
                'QAF_FAIL_FAST', 'QAF_CONTINUE_ON_ERROR', 'QAF_TIMEOUT_MINUTES',
                'QAF_RETRY_COUNT', 'QAF_RETRY_DELAY', 'QAF_PARALLEL', 'QAF_PARALLEL_JOBS'
            ]
        },
        output_formats=os.getenv('QAF_OUTPUT_FORMATS', 'allure,junit').split(','),
        report_artifacts=os.getenv('QAF_ARTIFACTS', 'reports/allure-results,reports/test_reports').split(','),
        notification_webhooks=os.getenv('QAF_WEBHOOKS', '').split(',') if os.getenv('QAF_WEBHOOKS') else []
    )