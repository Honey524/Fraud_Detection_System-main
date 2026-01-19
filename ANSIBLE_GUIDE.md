# Ansible Integration Guide for Fraud Detection System

## 📋 Table of Contents
1. [What is Ansible](#what-is-ansible)
2. [Why We Need Ansible](#why-we-need-ansible)
3. [Architecture Overview](#architecture-overview)
4. [Installation & Setup](#installation--setup)
5. [Configuration Files](#configuration-files)
6. [Running Playbooks](#running-playbooks)
7. [Detailed Use Cases](#detailed-use-cases)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## What is Ansible?

**Ansible** is an open-source **infrastructure automation platform** that:
- ✅ Automates repetitive tasks across multiple servers
- ✅ Deploys applications consistently
- ✅ Manages configuration at scale
- ✅ Requires NO agent installation (agentless)
- ✅ Uses simple YAML syntax (easy to learn)
- ✅ Provides idempotent operations (safe to run repeatedly)

### Key Concepts

| Term | Meaning |
|------|---------|
| **Playbook** | YAML file containing automation logic (like a script) |
| **Role** | Reusable automation component (like a function) |
| **Task** | Individual unit of work (like a command) |
| **Inventory** | List of servers you want to manage |
| **Module** | Built-in Ansible function (apt, docker, kubectl, etc.) |
| **Handler** | Task triggered by other tasks |

---

## Why We Need Ansible

### Problem: Manual Server Management ❌
```
Developer 1: Setup server manually → Takes 2 hours, errors happen
Developer 2: Setup same server → Takes 3 hours, different setup
Production: Deploy manually → Mistakes, inconsistency, slow
```

### Solution: Ansible Automation ✅
```
ansible-playbook playbooks/setup.yml → All servers identical setup in 30 mins
ansible-playbook playbooks/deploy-docker.yml → Deploy to 10 servers simultaneously
ansible-playbook playbooks/health-check.yml → Monitor all services instantly
```

### Our Benefits in This Project

| Challenge | Ansible Solution |
|-----------|------------------|
| Complex multi-service deployment | One command deploys all 7 services |
| Manual configuration errors | Automated, validated configuration |
| Inconsistent environments | All servers configured identically |
| Manual monitoring | Automated health checks |
| Disaster recovery | Automated backups with versioning |
| Scaling to multiple servers | Deploy to 100 servers with same playbook |
| CI/CD Pipeline | Integrate with Jenkins, GitLab CI |

---

## Architecture Overview

### Current Project Structure

```
Fraud Detection System
├── Services (7 total)
│   ├── ML Service (Flask)
│   ├── Alert Service (Flask)
│   ├── Web UI (Flask)
│   ├── Kafka Broker
│   ├── Zookeeper
│   ├── Producer
│   └── Spark
│
├── Deployment Options
│   ├── Docker Compose (single server)
│   └── Kubernetes (production cluster)
│
└── Ansible Automation
    ├── Setup servers
    ├── Deploy Docker/K8s
    ├── Monitor health
    └── Backup/Recovery
```

### Deployment Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  ANSIBLE WORKFLOW                            │
└──────────────────────────────────────────────────────────────┘

Step 1: SETUP
ansible-playbook playbooks/setup.yml
├─ Updates OS packages
├─ Installs dependencies
├─ Creates directories
└─ Configures system

Step 2: DEPLOY (Choose One)

  Option A: DOCKER COMPOSE
  ansible-playbook playbooks/deploy-docker.yml
  ├─ Installs Docker
  ├─ Builds images
  ├─ Starts containers
  └─ Verifies health

  Option B: KUBERNETES
  ansible-playbook playbooks/deploy-k8s.yml
  ├─ Installs kubectl
  ├─ Applies manifests
  ├─ Creates namespaces
  └─ Verifies pods

Step 3: MONITORING
ansible-playbook playbooks/health-check.yml
├─ Checks service status
├─ Collects metrics
└─ Generates reports

Step 4: BACKUP
ansible-playbook playbooks/backup.yml
├─ Backs up data
├─ Compresses archives
└─ Cleans old backups
```

---

## Installation & Setup

### Step 1: Install Ansible

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y ansible
ansible --version  # Should show 2.9+
```

**On macOS:**
```bash
brew install ansible
ansible --version
```

**Using pip (any OS):**
```bash
pip install ansible
pip install kubernetes  # For K8s module
```

### Step 2: Verify SSH Access

Ansible communicates with servers over SSH. Verify you can access:

```bash
# For localhost (development)
sudo -l  # Check sudo access

# For remote servers
ssh -i ~/.ssh/id_rsa ubuntu@your-server-ip
```

### Step 3: Configure Ansible

The project already includes `ansible/ansible.cfg` which:
- ✅ Sets inventory file location
- ✅ Configures SSH options
- ✅ Enables Python 3
- ✅ Sets parallel execution (forks)
- ✅ Enables fact caching (faster runs)

---

## Configuration Files

### 1. **ansible.cfg** - Ansible Settings

**Location:** `ansible/ansible.cfg`

```ini
[defaults]
inventory = inventory/hosts.ini              # Where to find servers
forks = 5                                    # Run on 5 servers in parallel
timeout = 30                                 # Connection timeout
interpreter_python = /usr/bin/python3       # Use Python 3

[privilege_escalation]
become = True                                # Use sudo for admin tasks
become_method = sudo                         # Use sudo (not su)

[ssh_connection]
pipelining = True                            # Reduce SSH overhead
```

**Why Important:**
- Performance: `forks = 5` means run on 5 servers simultaneously
- Compatibility: `interpreter_python` ensures correct Python used
- Security: `become = True` allows privilege escalation

### 2. **hosts.ini** - Server Inventory

**Location:** `ansible/inventory/hosts.ini`

**What it defines:**
- Which servers to manage
- Server groups (docker_hosts, k8s_masters, etc.)
- Connection details (IP, username, port)

**Example content:**
```ini
[docker_hosts]
localhost ansible_connection=local          # Local machine
docker-prod-1 ansible_host=192.168.1.10    # Remote server
docker-prod-2 ansible_host=192.168.1.11    # Another server

[k8s_masters]
localhost ansible_connection=local
k8s-master-1 ansible_host=192.168.1.20
```

**Usage:**
```bash
# Run on localhost only
ansible-playbook playbooks/deploy-docker.yml -i inventory/hosts.ini -l localhost

# Run on all docker hosts
ansible-playbook playbooks/deploy-docker.yml -i inventory/hosts.ini -l docker_hosts

# Run on specific host
ansible-playbook playbooks/deploy-docker.yml -i inventory/hosts.ini -l docker-prod-1
```

### 3. **group_vars/** - Variable Files

**Location:** `ansible/group_vars/`

These YAML files store variables used in playbooks:

**all.yml** - Applied to ALL servers
```yaml
project_name: Fraud Detection System
project_root: /opt/fraud-detection-system
python_version: "3.10"
timezone: UTC

app_ports:
  ml_service: 5000
  alert_service: 5001
  web_ui: 8000
  kafka: 9092
```

**docker_hosts.yml** - Applied only to docker_hosts group
```yaml
docker_version: "24.0"
docker_compose_version: "2.20"
service_replicas: 1
```

**k8s_masters.yml** - Applied only to k8s_masters group
```yaml
k8s_version: "1.31.0"
k8s_namespace: fraud-detection
```

**Why Variables?**
- Centralized configuration
- Reusable across multiple playbooks
- Easy to change without editing playbooks
- Different values for different environments

---

## Running Playbooks

### Quick Start Commands

**1. Initial Setup (Run Once)**
```bash
cd ansible/
ansible-playbook playbooks/setup.yml
```

**What it does:**
- Updates all system packages
- Installs Docker, kubectl, git, etc.
- Creates necessary directories
- Sets timezone and locale

**2. Deploy with Docker Compose**
```bash
ansible-playbook playbooks/deploy-docker.yml
```

**What it does:**
- Installs Docker and Docker Compose
- Builds container images
- Starts all 7 services
- Verifies health endpoints

**3. Deploy to Kubernetes**
```bash
ansible-playbook playbooks/deploy-k8s.yml
```

**What it does:**
- Installs kubectl, kubeadm, kubelet
- Applies K8s manifests
- Creates fraud-detection namespace
- Waits for all pods to be ready

**4. Health Check**
```bash
ansible-playbook playbooks/health-check.yml
```

**What it does:**
- Checks all services status
- Collects system metrics
- Shows service logs
- Generates health report

**5. Backup Data**
```bash
ansible-playbook playbooks/backup.yml
```

**What it does:**
- Stops services cleanly
- Backs up project files
- Backs up Docker volumes
- Cleans old backups (>30 days)

### Advanced Usage

**Run on specific hosts only:**
```bash
ansible-playbook playbooks/deploy-docker.yml -l docker-prod-1
ansible-playbook playbooks/deploy-docker.yml -l docker_hosts  # All in group
```

**Run specific tags:**
```bash
ansible-playbook playbooks/setup.yml --tags=docker-install   # Only Docker
ansible-playbook playbooks/setup.yml --tags=docker-install,k8s-install  # Both
```

**Skip certain tasks:**
```bash
ansible-playbook playbooks/setup.yml --skip-tags=apt-packages  # Skip package updates
```

**Dry-run (see what would happen):**
```bash
ansible-playbook playbooks/deploy-docker.yml --check
```

**Verbose output:**
```bash
ansible-playbook playbooks/deploy-docker.yml -vvv  # Very verbose
ansible-playbook playbooks/deploy-docker.yml -v    # Normal verbose
```

**List tasks without running:**
```bash
ansible-playbook playbooks/deploy-docker.yml --list-tasks
```

**Run with extra variables:**
```bash
ansible-playbook playbooks/deploy-docker.yml \
  -e "docker_version=24.0" \
  -e "project_root=/custom/path"
```

---

## Detailed Use Cases

### Use Case 1: Setup New Development Machine

**Scenario:** Team member gets new laptop, needs full setup

**Steps:**
```bash
# 1. Update inventory to add your machine
nano ansible/inventory/hosts.ini
# Add: mydev-machine ansible_connection=local

# 2. Run setup playbook
ansible-playbook playbooks/setup.yml -l mydev-machine

# 3. Deploy services
ansible-playbook playbooks/deploy-docker.yml -l mydev-machine

# 4. Verify health
ansible-playbook playbooks/health-check.yml -l mydev-machine
```

**Result:** New machine fully configured with all services running in <30 minutes

---

### Use Case 2: Deploy to 5 Production Servers

**Scenario:** Release to production servers simultaneously

**Inventory setup:**
```ini
[docker_hosts]
prod-1 ansible_host=10.0.0.1 ansible_user=ubuntu
prod-2 ansible_host=10.0.0.2 ansible_user=ubuntu
prod-3 ansible_host=10.0.0.3 ansible_user=ubuntu
prod-4 ansible_host=10.0.0.4 ansible_user=ubuntu
prod-5 ansible_host=10.0.0.5 ansible_user=ubuntu
```

**Deployment:**
```bash
# Setup all servers in parallel
ansible-playbook playbooks/setup.yml -l docker_hosts

# Deploy to all servers simultaneously
ansible-playbook playbooks/deploy-docker.yml -l docker_hosts

# Verify all servers
ansible-playbook playbooks/health-check.yml -l docker_hosts
```

**Benefit:** All 5 servers deployed identically in ~45 minutes vs 5 hours manual

---

### Use Case 3: Roll Back Deployment

**Scenario:** New deployment has issues, need to revert

**Solution:**
```bash
# 1. Backup current state (if not already done)
ansible-playbook playbooks/backup.yml

# 2. Restore from previous backup
ansible docker_hosts -m shell -a \
  "cd {{ project_root }} && tar xzf backup/fraud-detection-backup-20240113.tar.gz"

# 3. Restart services
ansible docker_hosts -m shell -a \
  "docker compose -f {{ docker_compose_file }} restart"

# 4. Verify health
ansible-playbook playbooks/health-check.yml
```

---

### Use Case 4: Monitor All Services Daily

**Scenario:** Run daily health checks at 2 AM

**Setup cron job:**
```bash
# Edit crontab
crontab -e

# Add this line:
0 2 * * * cd /opt/fraud-detection-system/ansible && ansible-playbook playbooks/health-check.yml
```

**Result:** Every morning, you get a health report in logs/health_report_*.txt

---

### Use Case 5: Patch All Servers

**Scenario:** Security updates available, apply to all servers

**Create playbook** `ansible/playbooks/patch.yml`:
```yaml
---
- name: Patch all servers
  hosts: all
  become: yes
  
  tasks:
    - name: Update packages
      apt:
        update_cache: yes
        upgrade: dist
    
    - name: Restart if needed
      reboot:
        reboot_timeout: 300
      when: ansible_reboot_required
```

**Run it:**
```bash
ansible-playbook playbooks/patch.yml -l docker_hosts
```

---

## Best Practices

### 1. Use Inventory Groups

❌ **BAD:**
```bash
ansible-playbook playbooks/deploy-docker.yml -l 192.168.1.10
ansible-playbook playbooks/deploy-docker.yml -l 192.168.1.11
# Runs twice separately
```

✅ **GOOD:**
```bash
# In inventory/hosts.ini:
[docker_hosts]
prod-1 ansible_host=192.168.1.10
prod-2 ansible_host=192.168.1.11

# Run once for both:
ansible-playbook playbooks/deploy-docker.yml -l docker_hosts
```

### 2. Use Variables, Not Hard-coded Values

❌ **BAD:**
```yaml
- name: Start service
  command: docker compose -f /opt/fraud-detection-system/docker-compose.yml up -d
```

✅ **GOOD:**
```yaml
- name: Start service
  command: docker compose -f "{{ docker_compose_file }}" up -d
  # Defined in group_vars/all.yml
```

### 3. Use Handlers for Dependent Tasks

❌ **BAD:**
```yaml
- name: Copy config
  copy: src=config.yml dest=/etc/app/config.yml

- name: Restart service
  service: name=app state=restarted
```

✅ **GOOD:**
```yaml
- name: Copy config
  copy: src=config.yml dest=/etc/app/config.yml
  notify: restart app

handlers:
  - name: restart app
    service: name=app state=restarted
    # Only restarts if config changed
```

### 4. Use Tags for Partial Execution

```yaml
tasks:
  - name: Install Docker
    # ... docker install tasks ...
    tags: docker-install
    
  - name: Deploy services
    # ... deploy tasks ...
    tags: docker-deploy
```

**Usage:**
```bash
# Only install Docker
ansible-playbook playbooks/deploy-docker.yml --tags docker-install

# Skip Docker install
ansible-playbook playbooks/deploy-docker.yml --skip-tags docker-install
```

### 5. Use Become for Privilege Escalation

```yaml
tasks:
  - name: Install packages
    apt:
      name: docker.io
      state: present
    become: yes          # Use sudo
    become_user: root    # Become root

  - name: Regular user task
    command: whoami
    # No become, runs as regular user
```

### 6. Use Idempotent Modules

✅ **IDEMPOTENT** (safe to run repeatedly):
```yaml
- apt: name=docker.io state=present      # Install if not present
- service: name=docker state=started      # Start if not started
- file: path=/opt/app state=directory     # Create if doesn't exist
```

❌ **NOT IDEMPOTENT**:
```yaml
- shell: apt-get install docker.io        # Installs every time!
- shell: service docker start             # Errors if already started
- shell: mkdir /opt/app                   # Errors if exists
```

### 7. Use Meaningful Task Names

❌ **BAD:**
```yaml
- task1
- task2
- task3
```

✅ **GOOD:**
```yaml
- name: Install Docker CE from official repository
- name: Start Docker daemon and enable on boot
- name: Verify Docker installation by running hello-world
```

### 8. Add Comments Explaining Why

```yaml
# REASON: Docker must run as root to access system resources
- name: Ensure docker group exists for non-root access
  group:
    name: docker
    state: present
```

### 9. Use Retry Mechanisms

```yaml
- name: Wait for service to be ready
  uri:
    url: http://localhost:5000/health
    method: GET
  retries: 5          # Try 5 times
  delay: 10           # Wait 10 seconds between tries
  register: result
  until: result.status == 200  # Until succeeds
```

### 10. Always Add Error Handling

```yaml
- name: Non-critical task
  command: docker compose ps
  register: result
  ignore_errors: yes          # Don't fail if this errors

- name: Show result
  debug:
    msg: "{{ result.stdout | default('Service not running') }}"
```

---

## Troubleshooting

### Problem 1: Permission Denied Error

**Error:**
```
fatal: [localhost]: FAILED! => {"msg": "...permission denied..."}
```

**Solution:**
```bash
# Option 1: Run with sudo
ansible-playbook playbooks/setup.yml -K  # Asks for password

# Option 2: Add sudo permissions
sudo visudo
# Add: %ansible ALL=(ALL) NOPASSWD: ALL
```

### Problem 2: SSH Connection Timeout

**Error:**
```
fatal: [192.168.1.10]: UNREACHABLE! => {"msg": "timed out"}
```

**Solutions:**
```bash
# Check SSH connectivity
ssh -v ubuntu@192.168.1.10

# Test Ansible SSH
ansible all -i inventory/hosts.ini -m ping

# Update inventory with correct user
# In hosts.ini:
prod-1 ansible_host=192.168.1.10 ansible_user=ubuntu
```

### Problem 3: Python Not Found

**Error:**
```
Module python, python2, and python3 not found
```

**Solution:**
```bash
# Install Python 3
ansible all -i inventory/hosts.ini -m raw -a "apt-get install -y python3"

# Update ansible.cfg
interpreter_python = /usr/bin/python3
```

### Problem 4: Playbook Syntax Error

**Error:**
```
ERROR! Syntax Error while loading YAML
```

**Solution:**
```bash
# Validate YAML syntax
ansible-playbook playbooks/deploy-docker.yml --syntax-check

# Common issues:
# - Missing colons (:)
# - Incorrect indentation (must be 2 spaces)
# - Unquoted special characters
```

### Problem 5: Services Not Starting

**Debug:**
```bash
# Run playbook with verbose output
ansible-playbook playbooks/deploy-docker.yml -vvv

# Check service logs
ansible docker_hosts -m command -a "docker compose logs ml_service"

# Manual verification
ansible docker_hosts -m shell -a "docker ps | grep fraud"
```

### Problem 6: Slow Playbook Execution

**Solutions:**
```bash
# 1. Increase parallel forks
ansible-playbook playbooks/deploy-docker.yml -f 10  # 10 servers in parallel

# 2. Enable pipelining (in ansible.cfg)
pipelining = True

# 3. Skip fact gathering
ansible-playbook playbooks/deploy-docker.yml --gather-facts=no

# 4. Use tags to run only what you need
ansible-playbook playbooks/deploy-docker.yml --tags docker-deploy
```

### Problem 7: Docker Image Build Failures

**Debug:**
```bash
# Check Docker build logs
ansible docker_hosts -m command -a "docker compose build --no-cache ml_service"

# Manual build to see full output
ansible docker_hosts -m shell -a "cd {{ project_root }} && docker build -f docker/ml_service.Dockerfile ."
```

---

## Useful Commands Reference

```bash
# List all hosts
ansible-inventory -i inventory/hosts.ini --list

# Test connectivity
ansible all -i inventory/hosts.ini -m ping

# Run adhoc command
ansible docker_hosts -i inventory/hosts.ini -m shell -a "docker ps"

# Check facts (system information)
ansible localhost -m setup | grep -i memory

# Get help on module
ansible-doc docker_compose_v2

# Validate syntax
ansible-playbook playbooks/deploy-docker.yml --syntax-check

# Dry run
ansible-playbook playbooks/deploy-docker.yml --check

# List tasks
ansible-playbook playbooks/deploy-docker.yml --list-tasks

# Run with custom inventory
ansible-playbook playbooks/deploy-docker.yml -i /path/to/custom/inventory

# Run on specific hosts
ansible-playbook playbooks/deploy-docker.yml -l "prod-1,prod-2"

# Increase verbosity
ansible-playbook playbooks/deploy-docker.yml -vvv  # Most verbose

# Pass variables from command line
ansible-playbook playbooks/deploy-docker.yml -e "docker_version=24.0"
```

---

## Next Steps

1. **Install Ansible** (if not already done)
2. **Update inventory** with your servers
3. **Run setup playbook**: `ansible-playbook playbooks/setup.yml`
4. **Deploy services**: `ansible-playbook playbooks/deploy-docker.yml`
5. **Monitor health**: `ansible-playbook playbooks/health-check.yml`
6. **Setup daily backups**: Add backup playbook to cron

---

## Additional Resources

- **Official Ansible Docs:** https://docs.ansible.com/
- **Module Reference:** https://docs.ansible.com/ansible/latest/modules/modules_by_category.html
- **Best Practices:** https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html
- **Community:** https://www.ansible.com/community

---

**Questions?** Check logs in `logs/` directory or run playbook with `-vvv` for verbose output.
