#!/usr/bin/env python3
"""
Deploy script for Stock Indicator API on AWS Linux.
Usage:
  python deploy.py          # interactive mode
  python deploy.py --install  # install deps and run
"""

import argparse
import os
import subprocess
import sys


def run(cmd, cwd=None):
    print(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def install_deps():
    print("=== Updating system packages ===")
    run("sudo yum update -y")

    print("=== Installing Python 3.12 + pip ===")
    run("sudo yum install -y python3.12 python3.12-pip")

    print("=== Installing project dependencies ===")
    run("python3.12 -m pip install --upgrade pip")
    run("python3.12 -m pip install -r requirements-api.txt")


def create_service():
    content = """[Unit]
Description=Stock Indicator API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/stock-api
ExecStart=/usr/bin/python3.12 -m uvicorn api:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
    path = "/etc/systemd/system/stock-api.service"
    print(f"=== Creating systemd service at {path} ===")
    subprocess.run(
        f'echo "{content}" | sudo tee {path}',
        shell=True, check=True
    )
    run("sudo systemctl daemon-reload")
    run("sudo systemctl enable stock-api")
    run("sudo systemctl start stock-api")
    run("sudo systemctl status stock-api --no-pager")


def open_firewall():
    print("=== Opening port 8000 in firewall ===")
    run("sudo firewall-cmd --zone=public --add-port=8000/tcp --permanent || true")
    run("sudo firewall-cmd --reload || true")
    print("NOTE: Also ensure AWS Security Group allows inbound TCP 8000 from your IP")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", action="store_true", help="Install deps only")
    parser.add_argument("--service", action="store_true", help="Create systemd service")
    parser.add_argument("--firewall", action="store_true", help="Open firewall port")
    args = parser.parse_args()

    if args.install:
        install_deps()
    if args.service:
        create_service()
    if args.firewall:
        open_firewall()

    if not any(vars(args).values()):
        install_deps()
        create_service()
        open_firewall()


if __name__ == "__main__":
    main()
