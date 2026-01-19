# Jenkins Complete Setup Guide

## Step 1: Initial Setup (First Time Only)

### 1.1 Access Jenkins UI
```bash
open http://localhost:8080
```

### 1.2 Unlock Jenkins
- Find initial admin password:
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```
- Paste password in "Administrator password" field

### 1.3 Install Suggested Plugins
- Click "Install suggested plugins"
- Wait ~10 minutes for installation

---

## Step 2: Install Essential Plugins

### 2.1 Automated Plugin Installation
```bash
chmod +x scripts/jenkins-install-plugins.sh
./scripts/jenkins-install-plugins.sh
docker restart jenkins
# Wait 5 minutes for startup
```

### 2.2 Manual Plugin Installation (If Automated Fails)
1. Manage Jenkins → Manage Plugins → Available
2. Search and install:
   - ✅ Pipeline: Declarative Agent API
   - ✅ Pipeline: Stage View
   - ✅ Git
   - ✅ Credentials Binding
   - ✅ Timestamper
   - ✅ Docker
   - ✅ Docker Pipeline
   - ✅ GitHub
   - ✅ AnsiColor
   - ✅ Email Extension
   - ✅ Slack Notification

---

## Step 3: Configure Credentials

### 3.1 Docker Registry Credentials
1. Manage Jenkins → Manage Credentials → System → Global credentials
2. Add Credentials:
   - Kind: Username with password
   - Scope: Global
   - Username: `your-docker-username` (Docker Hub username)
   - Password: `your-personal-access-token` (Generate from Docker Hub)
   - ID: `docker-registry-creds` (⚠️ **MUST match Jenkinsfile**)
   - Description: Docker Registry Credentials
3. Click Create

### 3.2 GitHub Credentials (Optional)
1. Add Credentials:
   - Kind: Username with password
   - Username: `your-github-username`
   - Password: `your-github-personal-access-token`
   - ID: `github-credentials`
   - Description: GitHub API Token
2. Click Create

### 3.3 Slack Webhook (Optional)
1. Add Credentials:
   - Kind: Secret text
   - Secret: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
   - ID: `slack-webhook`
   - Description: Slack Webhook URL
2. Click Create

---

## Step 4: Create Pipeline Job

### 4.1 Create New Job
1. New Item
2. Job name: `fraud-detection-ci-cd`
3. Type: Pipeline
4. Click OK

### 4.2 Configure Pipeline
1. General:
   - ✅ Enable: "This job can be checked out by Jenkins"
   - ✅ Enable: "GitHub project" (if using GitHub)
   - Project URL: `https://github.com/your-username/Fraud_Detection_System-main`

2. Build Triggers:
   - ✅ Check: GitHub hook trigger for GITscm polling
   - ✅ Check: Poll SCM (Cron: `H/15 * * * *` for every 15 minutes)

3. Advanced Project Options:
   - Quiet period: 10 seconds
   - Retry count: 3

4. Pipeline:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: `https://github.com/your-username/Fraud_Detection_System-main.git`
   - Credentials: (select GitHub credentials if created)
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`

5. Parameters (Optional):
   - Add Parameter: `PUSH_IMAGES`
     - Type: Boolean
     - Default: unchecked
     - Description: Push images to registry?
   - Add Parameter: `REGISTRY`
     - Type: String
     - Default value: `docker.io`
     - Description: Docker registry URL

6. Click Save

---

## Step 5: Configure Git Webhook (Automatic Builds)

### 5.1 For GitHub
1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. Configure:
   - Payload URL: `http://your-jenkins-host:8080/github-webhook/`
   - Content type: application/json
   - Events: Push events (or all events)
   - ✅ Active: checked
4. Click Add webhook

### 5.2 For GitLab
1. Go to your GitLab project
2. Settings → Integrations → Jenkins
3. Configure:
   - Jenkins URL: `http://your-jenkins-host:8080`
   - Project name: `fraud-detection-ci-cd`
   - Username: (optional)
   - Password: (optional)
4. Click Save

### 5.3 For Bitbucket
1. Go to repository Settings → Webhooks
2. Add webhook:
   - URL: `http://your-jenkins-host:8080/bitbucket-hook/`
   - Events: Repository push
   - Active: checked
3. Click Save

---

## Step 6: Configure Notifications

### 6.1 Email Notifications
1. Manage Jenkins → System Configuration
2. Scroll to E-mail Notification
3. Configure:
   - SMTP server: `smtp.gmail.com`
   - SMTP port: `587`
   - Use SMTP Authentication: ✅ checked
   - User name: `your-email@gmail.com`
   - Password: `your-app-specific-password` (generate in Google Account)
   - SMTP TLS: ✅ checked
   - Charset: UTF-8
4. Test configuration
5. Click Save

### 6.2 Slack Notifications
1. Manage Jenkins → Manage Plugins → Available
2. Search: "Slack Notification"
3. Install plugin
4. Manage Jenkins → System Configuration
5. Scroll to Slack
6. Configure:
   - Workspace: `your-workspace`
   - Credential: (select slack-webhook created earlier)
   - Default channel: `#jenkins-alerts`
   - Commit info in logs: ✅ checked
7. Click Save

---

## Step 7: Run First Build

### 7.1 Manual Trigger
1. Go to `fraud-detection-ci-cd` job
2. Click "Build with Parameters"
3. Set options:
   - PUSH_IMAGES: unchecked (for first test)
   - REGISTRY: docker.io
4. Click Build

### 7.2 Monitor Build
1. Click build number (e.g., `#1`)
2. Click "Console Output" to see real-time logs
3. Wait for pipeline to complete (5-15 minutes)
4. Expected output:
   ```
   ✅ Checkout
   ✅ Tests
   ✅ Lint & Security
   ✅ Build Images
   ✅ Start Services
   ✅ Health Checks
   ✅ Deploy (Ansible)
   ```

---

## Step 8: Verify Setup

### 8.1 Check Job Configuration
```bash
# Verify Jenkins can access Docker
docker exec jenkins docker ps

# Verify Jenkins can run builds
curl http://localhost:8080/api/json | grep -i "jobs"
```

### 8.2 Check Pipeline Execution
1. Go to Pipeline job
2. Click "Stages" tab to see visual pipeline
3. Each stage should show:
   - Stage name (Checkout, Tests, etc.)
   - Duration (how long stage took)
   - Status (✅ passed, ❌ failed, ⏭️ skipped)

### 8.3 Check Logs
1. Click build number
2. Click "Console Output"
3. Should see:
   - Git clone output
   - Test results (pytest)
   - Linting results (flake8, black)
   - Build output (docker compose build)
   - Health check results (curl responses)

---

## Step 9: Advanced Configuration (Optional)

### 9.1 Enable Configuration as Code (JCasC)
```bash
# Copy JCasC config to Jenkins home
cp jenkins/casc.yaml ./jenkins_home/casc.yaml

# Set environment variable
export CASC_JENKINS_CONFIG=/var/jenkins_home/casc.yaml

# Restart Jenkins
docker restart jenkins
```

### 9.2 Set Up Multibranch Pipeline
1. New Item
2. Job name: `fraud-detection-multibranch`
3. Type: Multibranch Pipeline
4. Branch Sources:
   - Add source: Git
   - Project Repository: `https://github.com/your-username/Fraud_Detection_System-main.git`
   - Behaviours:
     - Discover branches: All branches
     - Discover pull requests from origin
5. Scan Multibranch Pipeline Triggers:
   - Check: Periodically if not otherwise run
   - Interval: 1 minute
6. Click Save

### 9.3 Enable Build Status Reporting
- GitHub:
  ```bash
  Manage Jenkins → System Configuration → GitHub
  - Check: Manage hooks
  - GitHub API endpoint: https://api.github.com
  - Credentials: (select GitHub credentials)
  ```

---

## Troubleshooting

### Issue: Jenkinsfile Error "org.jenkinsci.plugins.workflow.common.StepException"
**Solution:**
1. Verify all plugins installed
2. Check Jenkinsfile syntax: `cat Jenkinsfile | grep -E "^\s+stage\("`
3. Reload Jenkins Configuration: Manage Jenkins → Reload Configuration from Disk

### Issue: Docker Build Fails "Cannot connect to Docker daemon"
**Solution:**
```bash
# Verify Jenkins has Docker access
docker exec jenkins docker ps

# If fails, ensure socket is mounted correctly in docker-compose.yml
# Check: volumes: - /var/run/docker.sock:/var/run/docker.sock
docker compose ps jenkins  # Verify jenkins container running
```

### Issue: Credentials Not Found
**Solution:**
1. Verify credential ID matches Jenkinsfile: `docker-registry-creds`
2. Manage Jenkins → Manage Credentials → Global
3. Ensure credential is in "Global credentials (unrestricted)" scope
4. Test credential: Click on credential → Test Connection (if applicable)

### Issue: Pipeline Timeout
**Solution:**
1. Edit job configuration
2. Advanced Project Options → Timeout:
   - Check: Abort the build if it's stuck for X minutes
   - Value: 90 (increased from default 60)
3. Or set in Jenkinsfile: `options { timeout(time: 90, unit: 'MINUTES') }`

### Issue: Health Check Endpoint Not Responding
**Solution:**
```bash
# Verify services are running
docker compose ps

# Check service logs
docker compose logs ml_service
docker compose logs alert_service

# Manually test endpoints
curl http://localhost:5000/health
curl http://localhost:5001/health
```

---

## Verification Checklist

- [ ] Jenkins running on port 8080
- [ ] Initial admin password obtained
- [ ] All plugins installed successfully
- [ ] Docker registry credentials created
- [ ] Pipeline job created with correct configuration
- [ ] GitHub webhook configured
- [ ] First build triggered and passed
- [ ] All stages completed successfully
- [ ] Health endpoints responding
- [ ] Build artifacts archived
- [ ] Notifications working (if configured)

---

## Quick Start Commands

```bash
# 1. Start everything
docker compose up -d

# 2. Wait for Jenkins to be ready
sleep 30

# 3. Get initial admin password
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 4. Open Jenkins UI
open http://localhost:8080

# 5. Install plugins automatically
chmod +x scripts/jenkins-install-plugins.sh
./scripts/jenkins-install-plugins.sh

# 6. Restart Jenkins to load plugins
docker restart jenkins

# 7. Create credentials in UI (see Step 3)

# 8. Create pipeline job in UI (see Step 4)

# 9. Trigger build
curl -X POST http://localhost:8080/job/fraud-detection-ci-cd/build \
  -u admin:PASSWORD
```

---

**🎉 Jenkins is now fully configured and ready for CI/CD!**

For more help, see: https://www.jenkins.io/doc/
