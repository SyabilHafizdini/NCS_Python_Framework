def after_scenario(context, scenario):
    """Clean up after each scenario"""
    if hasattr(context, 'driver'):
        context.driver.quit()


def after_all(context):
    """Generate two separate Allure HTML reports"""
    import subprocess
    import os
    import shutil
    from datetime import datetime
    
    if os.path.exists('reports/allure-results'):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 1. Generate CURRENT EXECUTION ONLY report from fresh allure-results
            current_output_dir = f"reports/test_reports/{timestamp}"
            os.makedirs(current_output_dir, exist_ok=True)
            
            subprocess.run([
                'allure', 'generate', '--single-file',
                'reports/allure-results', '-o', current_output_dir
            ], check=True, shell=True)
            print(f"Current execution report: {current_output_dir}/index.html")
            
            # 2. MOVE current results to history for accumulation
            history_dir = "reports/allure-history"
            os.makedirs(history_dir, exist_ok=True)
            
            # Move all files from allure-results to allure-history
            for item in os.listdir('reports/allure-results'):
                src = os.path.join('reports/allure-results', item)
                if os.path.isfile(src):
                    # Keep original name but add timestamp if duplicate exists
                    dst = os.path.join(history_dir, item)
                    if os.path.exists(dst):
                        name, ext = os.path.splitext(item)
                        dst = os.path.join(history_dir, f"{name}_{timestamp}{ext}")
                    shutil.move(src, dst)  # MOVE not copy
            
            # 3. Generate full history report from accumulated data
            temp_history_output = f"reports/temp_history_{timestamp}"
            subprocess.run([
                'allure', 'generate', '--single-file',
                history_dir, '-o', temp_history_output
            ], check=True, shell=True)
            
            # Move to final location
            if os.path.exists(f'{temp_history_output}/index.html'):
                if os.path.exists('reports/full-execution-history.html'):
                    os.remove('reports/full-execution-history.html')
                shutil.move(f'{temp_history_output}/index.html', 'reports/full-execution-history.html')
                shutil.rmtree(temp_history_output)
                print("Full execution history report: reports/full-execution-history.html")
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Failed to generate Allure report. Ensure Allure CLI is installed.")