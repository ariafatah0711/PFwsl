# PFwsl
## Port forwarding wsl (Windows Subsystem Linux)

<p align="center">
  <a href="#description">description</a> •
  <a href="#table-of-contents">table of contents</a> •
  <a href="#download">Download</a> •
  <a href="#related">Related</a> •
  <a href="#license">License</a>
</p>

<p id="description"></p>

## 🚀 Description
- PFwsl is a Python-based automation tool designed to simplify port forwarding on Windows Subsystem for Linux (WSL). This tool helps users set up and manage port forwarding configurations between WSL and Windows environments. It automates the process of forwarding specific ports, which is useful for developers or network administrators who need to route traffic from their WSL instance to the host machine.

<p id="table-of-contents"></p>

## 📋 Table of Contents
<details open>
  <summary><b>installasion</b></summary>

  ```bash
  git clone https://github.com/ariafatah0711/PFwsl
  cd PFwsl
  pip3 install -r req.txt
  ```
</details>

<details open>
  <summary><b>how to use</b></summary>

  ```
usage: app.py [-h] [-I interface] [-p portProxy [portProxy ...]] [-l local ip] [-r remote ip] [-v] [action]

Automation Port Forwarding for WSL (Windows Subsystem for Linux)

positional arguments:
  action                specify action

options:
  -h, --help            show this help message and exit
  -I interface, --interface interface
                        enter network interface
  -p portProxy [portProxy ...], --port portProxy [portProxy ...]
                        enter ports in the format <listen_port>:<connect_port>
  -l local ip           enter local IP address
  -r remote ip          enter remote IP address
  -v                    verbose mode
  ```
</details>

<details open>
  <summary><b>example</b></summary>

  ```
Action:
  python3 app.py show
  python3 app.py reset

Example:
  python3 app.py 8080:8080
  python3 app.py -l 192.168.10.1 -r 172.27.139.111 -p 8081:2000
  python3 app.py -I Ethernet -p 8081:8081 8082:8082
  ```
</details>

<p id="download"></p>

## 🔨 Download

1. Open a terminal or command prompt on your computer.
2. Navigate to the directory where you want to save this project.
3. Use the following command to download the project from the GitHub repository:
```sh
git clone https://github.com/ariafatah0711/PFwsl.git
cd PFwsl
pip3 install -r req.txt
```

<p id="related"></p>

## 📈 related
<!-- <a href="https://ariafatah0711.github.io/PFwsl/" alt="DEMO"><img src="https://img.shields.io/static/v1?style=for-the-badge&label=DEMO&message=WEB&color=000000"></a> -->

<p id="license"></p>

## ©️ license
<a href="https://github.com/ariafatah0711" alt="CREATED"><img src="https://img.shields.io/static/v1?style=for-the-badge&label=CREATED%20BY&message=ariafatah0711&color=000000"></a>
<a href="https://github.com/ariafatah0711/PFwsl/blob/main/LICENSE" alt="LICENSE"><img src="https://img.shields.io/static/v1?style=for-the-badge&label=LICENSE&message=APACHE&color=000000"></a>