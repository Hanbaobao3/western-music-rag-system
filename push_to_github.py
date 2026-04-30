#!/usr/bin/env python3
"""
Push to GitHub script for Western Music History RAG System
"""
import subprocess
import sys

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"Running: {description}")
    print(f"Command: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False

def main():
    print("=" * 70)
    print("Western Music History RAG System - Push to GitHub")
    print("=" * 70)
    print()

    # 1. 确保main分支
    print("Step 1: Setting up main branch...")
    run_command("git branch -M main", "Rename master to main branch")

    # 2. 检查是否已配置remote
    print("Step 2: Checking remote configuration...")
    try:
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, check=True)
        if "origin" in result.stdout:
            print("Remote 'origin' already configured")
            print(f"Current remote: {result.stdout.strip()}")
            use_existing = True
        else:
            print("Remote 'origin' not found")
            use_existing = False
    except:
        use_existing = False

    # 3. 添加remote（如果需要）
    if not use_existing:
        print("Step 3: Please add GitHub remote")
        print("Run this command:")
        print("  git remote add origin https://github.com/YOUR_USERNAME/western-music-rag-system.git")
        print()
        print("Replace YOUR_USERNAME with your actual GitHub username")
        print("Then run this script again")
        return

    # 4. 推送到GitHub
    print("Step 4: Pushing to GitHub...")
    success = run_command(
        "git push -u origin main",
        "Push code to GitHub"
    )

    if success:
        print()
        print("=" * 70)
        print("Upload Complete!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Check your GitHub repository")
        print("2. Deploy on Render: https://dashboard.render.com/")
        print("3. Connect your GitHub repository in Render")
        print("4. Configure and deploy as Web Service")
        print()
        print("Your repository URL will be:")
        print("  https://github.com/Hanbaobao3/western-music-rag-system")

if __name__ == "__main__":
    main()
