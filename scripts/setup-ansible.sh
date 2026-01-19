#!/bin/bash

# Ansible Quick Start Script
# This script helps you get started with Ansible for the Fraud Detection System

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ANSIBLE_DIR="$SCRIPT_DIR/ansible"
PROJECT_ROOT="/opt/fraud-detection-system"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "\n${BLUE}═════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Main script
main() {
    print_header "Ansible Setup for Fraud Detection System"
    
    # Check if Ansible is installed
    if ! command -v ansible &> /dev/null; then
        print_error "Ansible not found. Installing..."
        
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y ansible
        elif command -v brew &> /dev/null; then
            brew install ansible
        else
            print_error "Unable to install Ansible. Please install manually."
            exit 1
        fi
    fi
    
    print_success "Ansible is installed: $(ansible --version | head -1)"
    
    # Install Python Kubernetes module for K8s operations
    print_header "Installing Dependencies"
    pip install --upgrade ansible kubernetes pyyaml
    print_success "Dependencies installed"
    
    # Check connectivity
    print_header "Testing Inventory Connectivity"
    cd "$ANSIBLE_DIR"
    
    if ansible all -i inventory/hosts.ini -m ping 2>/dev/null | grep -q "SUCCESS"; then
        print_success "Connectivity test passed"
    else
        print_warning "Could not ping hosts. Make sure SSH is configured."
    fi
    
    # Show available playbooks
    print_header "Available Playbooks"
    echo -e "${GREEN}1. Setup - Initial server configuration${NC}"
    echo -e "   ${BLUE}ansible-playbook playbooks/setup.yml${NC}"
    echo ""
    echo -e "${GREEN}2. Deploy with Docker Compose${NC}"
    echo -e "   ${BLUE}ansible-playbook playbooks/deploy-docker.yml${NC}"
    echo ""
    echo -e "${GREEN}3. Deploy to Kubernetes${NC}"
    echo -e "   ${BLUE}ansible-playbook playbooks/deploy-k8s.yml${NC}"
    echo ""
    echo -e "${GREEN}4. Health Check${NC}"
    echo -e "   ${BLUE}ansible-playbook playbooks/health-check.yml${NC}"
    echo ""
    echo -e "${GREEN}5. Backup Data${NC}"
    echo -e "   ${BLUE}ansible-playbook playbooks/backup.yml${NC}"
    echo ""
    
    # Show next steps
    print_header "Next Steps"
    echo "1. Update inventory with your servers:"
    echo -e "   ${BLUE}nano $ANSIBLE_DIR/inventory/hosts.ini${NC}"
    echo ""
    echo "2. Update variables for your environment:"
    echo -e "   ${BLUE}nano $ANSIBLE_DIR/group_vars/all.yml${NC}"
    echo ""
    echo "3. Run the setup playbook:"
    echo -e "   ${BLUE}cd $ANSIBLE_DIR${NC}"
    echo -e "   ${BLUE}ansible-playbook playbooks/setup.yml${NC}"
    echo ""
    echo "4. Deploy your services:"
    echo -e "   ${BLUE}ansible-playbook playbooks/deploy-docker.yml${NC}"
    echo "   ${BLUE}OR${NC}"
    echo -e "   ${BLUE}ansible-playbook playbooks/deploy-k8s.yml${NC}"
    echo ""
    
    print_header "Documentation"
    echo "For detailed guide, see: ANSIBLE_GUIDE.md"
    echo ""
    
    print_success "Ansible setup complete! Ready to automate your infrastructure."
}

# Run main function
main "$@"
