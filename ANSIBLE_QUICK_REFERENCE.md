╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    ANSIBLE QUICK REFERENCE CARD                             ║
║                    Fraud Detection System                                    ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝


🚀 QUICK START (3 STEPS)
════════════════════════════════════════════════════════════════════════════════

1️⃣  INSTALL ANSIBLE:
   bash scripts/setup-ansible.sh

2️⃣  UPDATE SERVERS (edit ansible/inventory/hosts.ini):
   [docker_hosts]
   localhost ansible_connection=local
   my-server ansible_host=192.168.1.10 ansible_user=ubuntu

3️⃣  RUN PLAYBOOKS:
   cd ansible/
   ansible-playbook playbooks/setup.yml              # Setup servers
   ansible-playbook playbooks/deploy-docker.yml      # Deploy with Docker
   ansible-playbook playbooks/health-check.yml       # Check health


📊 5 PLAYBOOKS AVAILABLE
════════════════════════════════════════════════════════════════════════════════

│ PLAYBOOK             │ PURPOSE                    │ TIME   │ FREQUENCY  │
├──────────────────────┼────────────────────────────┼────────┼────────────┤
│ setup.yml            │ Initial server setup       │ 10min  │ Once       │
│ deploy-docker.yml    │ Deploy with Docker Compose │ 20min  │ Per change │
│ deploy-k8s.yml       │ Deploy with Kubernetes     │ 30min  │ Per change │
│ health-check.yml     │ Monitor service health     │ 5min   │ Daily      │
│ backup.yml           │ Backup data & volumes      │ 15min  │ Daily      │


🎯 5 ROLES (REUSABLE COMPONENTS)
════════════════════════════════════════════════════════════════════════════════

docker-install/    → Install Docker & Docker Compose
docker-deploy/     → Deploy all services with Docker Compose
k8s-install/       → Install kubectl, kubeadm, kubelet
k8s-deploy/        → Deploy services to Kubernetes cluster
monitoring/        → Health checks & system monitoring


📁 DIRECTORY STRUCTURE
════════════════════════════════════════════════════════════════════════════════

ansible/
├── ansible.cfg                      # Ansible configuration
├── inventory/
│   └── hosts.ini                   # Your servers go here ⭐
├── group_vars/
│   ├── all.yml                     # All servers variables
│   ├── docker_hosts.yml            # Docker-specific variables
│   └── k8s_masters.yml             # Kubernetes-specific variables
├── playbooks/
│   ├── setup.yml                   # Initial setup
│   ├── deploy-docker.yml           # Docker deployment
│   ├── deploy-k8s.yml              # Kubernetes deployment
│   ├── health-check.yml            # Health monitoring
│   └── backup.yml                  # Backup & recovery
└── roles/
    ├── docker-install/tasks/main.yml
    ├── docker-deploy/tasks/main.yml
    ├── k8s-install/tasks/main.yml
    ├── k8s-deploy/tasks/main.yml
    └── monitoring/tasks/main.yml


⚡ COMMAND CHEAT SHEET
════════════════════════════════════════════════════════════════════════════════

# RUN ENTIRE PLAYBOOK
ansible-playbook playbooks/deploy-docker.yml

# RUN ON SPECIFIC HOSTS ONLY
ansible-playbook playbooks/deploy-docker.yml -l localhost
ansible-playbook playbooks/deploy-docker.yml -l docker-prod-1

# RUN SPECIFIC TAGS
ansible-playbook playbooks/setup.yml --tags docker-install
ansible-playbook playbooks/setup.yml --tags k8s-install

# SKIP CERTAIN TASKS
ansible-playbook playbooks/setup.yml --skip-tags apt-packages

# DRY RUN (PREVIEW)
ansible-playbook playbooks/deploy-docker.yml --check

# VERBOSE OUTPUT
ansible-playbook playbooks/deploy-docker.yml -v
ansible-playbook playbooks/deploy-docker.yml -vvv

# LIST TASKS
ansible-playbook playbooks/deploy-docker.yml --list-tasks

# TEST CONNECTIVITY
ansible all -i inventory/hosts.ini -m ping

# RUN COMMAND ON HOSTS
ansible docker_hosts -m command -a "docker ps"
ansible all -m shell -a "uptime"

# OVERRIDE VARIABLES
ansible-playbook playbooks/deploy-docker.yml -e "docker_version=24.0"

# RUN WITH MULTIPLE PARALLEL SERVERS
ansible-playbook playbooks/setup.yml -f 10


📋 IMPORTANT FILES TO EDIT
════════════════════════════════════════════════════════════════════════════════

✏️  ansible/inventory/hosts.ini
   ├─ Add your server IP addresses
   ├─ Set SSH username
   └─ Organize into groups
   
   Example:
   [docker_hosts]
   prod-1 ansible_host=192.168.1.10 ansible_user=ubuntu
   
   [k8s_masters]
   k8s-master ansible_host=192.168.1.20 ansible_user=ubuntu


✏️  ansible/group_vars/all.yml
   ├─ Project settings: name, path, ports
   ├─ Python version
   ├─ Timezone
   ├─ Backup schedule
   └─ Notification settings
   
   Example changes:
   project_root: /custom/path
   timezone: America/New_York
   backup_schedule: "0 3 * * *"


✏️  ansible/group_vars/docker_hosts.yml
   ├─ Docker version
   ├─ Service replicas (for scaling)
   ├─ Resource limits
   └─ Log retention
   
   Example changes:
   docker_version: "25.0"
   ml_service_replicas: 3


✏️  ansible/group_vars/k8s_masters.yml
   ├─ Kubernetes version
   ├─ Cluster name
   ├─ Network CIDR
   └─ Storage configuration


🔄 WORKFLOW EXAMPLES
════════════════════════════════════════════════════════════════════════════════

SCENARIO 1: First-Time Deployment
──────────────────────────────────
$ cd ansible/
$ ansible-playbook playbooks/setup.yml                    # Step 1: Setup
$ ansible-playbook playbooks/deploy-docker.yml            # Step 2: Deploy
$ ansible-playbook playbooks/health-check.yml             # Step 3: Verify

Time: ~45 minutes for all servers


SCENARIO 2: Add New Server
──────────────────────────
1. Add to inventory/hosts.ini:
   [docker_hosts]
   new-server ansible_host=192.168.1.30 ansible_user=ubuntu

2. Run:
   ansible-playbook playbooks/setup.yml -l new-server
   ansible-playbook playbooks/deploy-docker.yml -l new-server

Time: ~30 minutes


SCENARIO 3: Deploy to 5 Servers in Parallel
─────────────────────────────────────────────
$ ansible-playbook playbooks/deploy-docker.yml -l docker_hosts

Automatic: Deploys to all servers simultaneously
Time: ~20 minutes (vs 100 minutes manual)


SCENARIO 4: Daily Automated Tasks
──────────────────────────────────
Add to crontab:
$ crontab -e

# Daily health check at 2 AM
0 2 * * * cd /path/to/project && ansible-playbook ansible/playbooks/health-check.yml

# Daily backup at 1 AM
0 1 * * * cd /path/to/project && ansible-playbook ansible/playbooks/backup.yml


🆘 TROUBLESHOOTING
════════════════════════════════════════════════════════════════════════════════

❌ "Permission denied"
   FIX: sudo visudo
        Add: %ansible ALL=(ALL) NOPASSWD: ALL

❌ "Host unreachable"
   FIX: Check: ssh -v ubuntu@192.168.1.10
        Update inventory with correct username/IP

❌ "Python not found"
   FIX: ansible all -m raw -a "apt-get install python3"
        Update ansible.cfg: interpreter_python = /usr/bin/python3

❌ "Syntax error"
   FIX: ansible-playbook playbooks/setup.yml --syntax-check
        Check: Indentation (2 spaces), colons after keys

❌ "Playbook too slow"
   FIX: Increase forks: ansible-playbook playbooks/setup.yml -f 10
        Enable pipelining in ansible.cfg: pipelining = True


📚 DOCUMENTATION
════════════════════════════════════════════════════════════════════════════════

Read these files for complete information:

1. ANSIBLE_GUIDE.md (700+ lines)
   ├─ What is Ansible
   ├─ Why you need it
   ├─ Detailed file explanations
   ├─ Usage examples
   ├─ Best practices
   └─ Troubleshooting

2. ANSIBLE_IMPLEMENTATION_SUMMARY.md
   └─ Overview of everything

3. Scripts
   └─ scripts/setup-ansible.sh
      └─ Automated Ansible installation


💡 KEY BENEFITS
════════════════════════════════════════════════════════════════════════════════

✅ Setup 5 servers in 10 minutes vs 10 hours manual
✅ All servers configured identically
✅ Automated backups every day
✅ Automated health checks every day
✅ One command deploys to 100 servers
✅ Easy recovery from failures
✅ Complete audit trail
✅ Team knowledge transfer via code


🔧 ANSIBLE CONCEPTS
════════════════════════════════════════════════════════════════════════════════

PLAYBOOK
└─ YAML file containing automation tasks
   Example: playbooks/deploy-docker.yml
   Usage: ansible-playbook playbooks/deploy-docker.yml

ROLE
└─ Reusable automation component
   Example: roles/docker-install/
   Usage: Imported in playbooks

TASK
└─ Individual unit of work
   Example: "Install Docker"
   Module: apt, docker, service, etc.

INVENTORY
└─ List of servers to manage
   Location: ansible/inventory/hosts.ini
   Format: [group_name] with servers listed below

VARIABLE
└─ Reusable values
   Location: ansible/group_vars/*.yml
   Usage: {{ variable_name }} in playbooks

MODULE
└─ Built-in Ansible function
   Examples: apt, docker, shell, command, kubernetes.core.k8s


🚀 NEXT STEPS
════════════════════════════════════════════════════════════════════════════════

1. ✅ Ansible is installed (from setup-ansible.sh)
2. ✅ All playbooks are configured
3. 👉 Update ansible/inventory/hosts.ini with YOUR servers
4. 👉 Customize ansible/group_vars/all.yml for YOUR environment
5. 👉 Run: ansible-playbook playbooks/setup.yml
6. 👉 Run: ansible-playbook playbooks/deploy-docker.yml
7. 👉 Monitor: ansible-playbook playbooks/health-check.yml


═══════════════════════════════════════════════════════════════════════════════

Need help? Run any playbook with -vvv for verbose output:
ansible-playbook playbooks/deploy-docker.yml -vvv

Questions? Check ANSIBLE_GUIDE.md!

═══════════════════════════════════════════════════════════════════════════════
