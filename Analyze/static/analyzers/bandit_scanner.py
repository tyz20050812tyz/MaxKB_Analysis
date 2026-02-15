import argparse
import subprocess
import os

def run_security_scan(target_path):
    print(f"启动 Bandit 安全漏洞扫描: {target_path}")
    os.makedirs('results', exist_ok=True)
    output_file = 'results/security_issues.json'
    
    command = [
        "bandit", "-r", target_path, "-f", "json", "-o", output_file, "-ll" 
    ]
    
    try:
        subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"安全扫描完成！报告已保存至 {output_file}")
    except FileNotFoundError:
        print("未找到 bandit 命令，请先执行 pip install bandit")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    args = parser.parse_args()
    run_security_scan(args.path)