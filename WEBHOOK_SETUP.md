# GitHub Webhook Configuration Guide

## 1. GitHub Webhook Setup

### Prerequisites
- GitHub repository with Jenkinsfile
- Jenkins running and accessible from GitHub
- GitHub credentials in Jenkins

### Step 1: Get Jenkins Webhook URL
```
http://your-jenkins-host:8080/github-webhook/
```

For local development:
```
http://localhost:8080/github-webhook/
# (Note: GitHub cannot reach localhost, use ngrok or Webhook Proxy)
```

### Step 2: Create GitHub Personal Access Token
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Token name: `jenkins-ci-cd`
4. Scopes:
   - ✅ repo (full control)
   - ✅ admin:repo_hook (write access to hooks)
   - ✅ admin:org_hook (if organization repo)
5. Click "Generate token"
6. **Copy token and save securely** (won't show again)

### Step 3: Add GitHub Credentials to Jenkins
1. Jenkins → Manage Jenkins → Manage Credentials
2. Global credentials → Add Credentials
3. Kind: Username with password
4. Username: `your-github-username`
5. Password: `paste-your-personal-access-token`
6. ID: `github-credentials`
7. Click Create

### Step 4: Add Webhook to GitHub Repository
1. Go to GitHub repository
2. Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL:** `http://your-jenkins-host:8080/github-webhook/`
   - **Content type:** application/json
   - **Events:**
     - ✅ Push events
     - ✅ Pull requests
     - ✅ Repository administration
   - **Active:** ✅ checked
4. Click "Add webhook"
5. GitHub will test the webhook (should see green checkmark)

### Step 5: Configure Jenkins Job
1. Jenkins → fraud-detection-ci-cd → Configure
2. Build Triggers:
   - ✅ Check: "GitHub hook trigger for GITScm polling"
3. Pipeline:
   - SCM: Git
   - Repository URL: `https://github.com/your-username/Fraud_Detection_System-main.git`
   - Credentials: Select "github-credentials"
   - Branch: `*/main`
4. Click Save

### Step 6: Test Webhook
Push a change to GitHub:
```bash
git add .
git commit -m "test webhook"
git push origin main
```

Jenkins should automatically start a build within seconds.

---

## 2. GitLab Webhook Setup

### Step 1: Create GitLab Personal Access Token
1. GitLab → Settings → Access Tokens
2. Token name: `jenkins-ci-cd`
3. Scopes:
   - ✅ api (complete read/write access)
   - ✅ read_user
4. Click "Create personal access token"
5. Copy and save token

### Step 2: Add GitLab Credentials to Jenkins
1. Jenkins → Manage Jenkins → Manage Credentials
2. Global credentials → Add Credentials
3. Kind: GitLab Personal Access Token
4. Token: `paste-your-gitlab-token`
5. ID: `gitlab-credentials`
6. Click Create

### Step 3: Configure Jenkins Job
1. Jenkins → fraud-detection-ci-cd → Configure
2. Pipeline:
   - SCM: Git
   - Repository URL: `https://gitlab.com/your-username/fraud-detection-system.git`
   - Credentials: Select "gitlab-credentials"
   - Branch: `*/main`
3. Build Triggers:
   - ✅ Check: "Push Events"
   - ✅ Check: "Merge Request Events"
4. Click Save

### Step 4: Add Webhook to GitLab Project
1. Go to GitLab project
2. Settings → Webhooks
3. URL: `http://your-jenkins-host:8080/gitlab/notifyCommit?token=GitLabApiToken`
4. Trigger events:
   - ✅ Push events
   - ✅ Merge request events
5. Click "Add webhook"
6. Click test (bell icon) → "Push events"

---

## 3. Bitbucket Webhook Setup

### Step 1: Create Bitbucket App Password
1. Bitbucket → Personal settings → App passwords
2. Click "Create app password"
3. Label: `jenkins-ci-cd`
4. Permissions:
   - ✅ account
   - ✅ repository
5. Click Create
6. Copy and save password

### Step 2: Add Bitbucket Credentials to Jenkins
1. Jenkins → Manage Jenkins → Manage Credentials
2. Global credentials → Add Credentials
3. Kind: Username with password
4. Username: `your-bitbucket-username`
5. Password: `paste-app-password`
6. ID: `bitbucket-credentials`
7. Click Create

### Step 3: Configure Jenkins Job
1. Jenkins → fraud-detection-ci-cd → Configure
2. Pipeline:
   - SCM: Git
   - Repository URL: `https://bitbucket.org/your-username/fraud-detection.git`
   - Credentials: Select "bitbucket-credentials"
   - Branch: `*/main`
3. Build Triggers:
   - ✅ Check: "Bitbucket repo:push" (if plugin installed)
4. Click Save

### Step 4: Add Webhook to Bitbucket
1. Go to repository Settings
2. Webhooks → Add webhook
3. Title: `Jenkins CI/CD`
4. URL: `http://your-jenkins-host:8080/bitbucket-hook/`
5. Events:
   - ✅ Repository push
   - ✅ Pull request created
   - ✅ Pull request updated
6. Click Save

---

## 4. Troubleshooting Webhooks

### Webhook Not Triggering

**Check 1: GitHub can reach Jenkins**
```bash
# From Jenkins container
docker exec jenkins curl -v http://your-host:8080/github-webhook/

# Should return: 200 OK or 403 Forbidden (not 404 or timeout)
```

**Check 2: Jenkins Plugin Installed**
```bash
# Verify GitHub plugin is installed
Jenkins → Manage Jenkins → Manage Plugins → Installed
# Search: "GitHub" - should be there
```

**Check 3: Repository Credentials**
```bash
# Jenkins → Manage Jenkins → Manage Credentials
# Verify you have GitHub credentials added
# Verify ID matches job configuration
```

**Check 4: Webhook Delivery**
- GitHub: Repository → Settings → Webhooks → Click webhook → "Recent Deliveries"
- GitLab: Project → Settings → Webhooks → Click webhook → "Recent events"
- Bitbucket: Repository → Settings → Webhooks → Click webhook → "View logs"

**Check 5: Increase Logging**
```bash
# Jenkins → Manage Jenkins → System Configuration
# Scroll to "Log Recorders"
# Add logger for: com.cloudbees.jenkins.GitHubSetupConnection
# Set level to FINE
# Trigger webhook and check logs
```

### Webhook Returns 403 Forbidden

**Solution:**
```bash
# Jenkins → Manage Jenkins → Configure Global Security
# CSRF Protection: ✅ Enable
# Uncheck: "Require POST requests to be sent with a CSRF token"
# Or install Strict Crumb Issuer plugin:
# - Manage Plugins → Available → "Strict Crumb Issuer"
# - Install and configure with exclusion list
```

### Webhook Payload Mismatch

**GitHub Example Verification:**
```bash
# GitHub → Settings → Webhooks → Click webhook
# Should see request body like:
{
  "ref": "refs/heads/main",
  "before": "...",
  "after": "...",
  "created": false,
  "deleted": false,
  "forced": false,
  "compare": "...",
  "commits": [...],
  "head_commit": {...}
}
```

---

## 5. Testing Webhooks Locally (using ngrok)

For local Jenkins development without public IP:

### Install ngrok
```bash
brew install ngrok  # macOS
# or download from https://ngrok.com/download
```

### Create Public URL
```bash
ngrok http 8080
```

Output:
```
Forwarding      https://your-id.ngrok.io -> http://localhost:8080
```

### Add to GitHub Webhook
1. GitHub → Settings → Webhooks
2. Payload URL: `https://your-id.ngrok.io/github-webhook/`
3. Click "Add webhook"

### Push and Test
```bash
git add .
git commit -m "test webhook"
git push origin main
```

Jenkins should trigger build automatically!

---

## 6. Webhook Security Best Practices

### Use Secret Tokens
```bash
# GitHub: Settings → Webhooks → Edit → Secret
# Generate secure token:
openssl rand -hex 32
# Save as GitHub secret
```

### Verify Webhook Signature
```groovy
// Add to Jenkinsfile if using GitHub secret
pipeline {
  triggers {
    githubPush()
  }
  options {
    // Webhook secret verification is automatic with plugin
  }
}
```

### Restrict Webhook Access
```bash
# Jenkins → Manage Jenkins → System Configuration
# Enable CSRF protection
# Create IP whitelist for webhook IPs:
# GitHub: https://api.github.com/meta
# GitLab: Check documentation
# Bitbucket: Check documentation
```

### Monitor Webhook Failures
```bash
# Create Jenkins job to monitor webhook status:
# Trigger: Periodically
# Script:
curl -s https://api.github.com/repos/YOUR_OWNER/YOUR_REPO/hooks \
  -H "Authorization: token YOUR_TOKEN" | \
  jq '.[] | select(.name=="web") | .deliveries'
```

---

## 7. Advanced Webhook Configuration

### Conditional Builds (Only Run on Main Branch)
```groovy
pipeline {
  triggers {
    githubPush()
  }
  stages {
    stage('Build') {
      when {
        branch 'main'
      }
      steps {
        // Build steps
      }
    }
  }
}
```

### Skip CI Commit Message
```bash
# In commit message, add:
git commit -m "fix: update deps [skip ci]"

# Jenkins will skip build if "[skip ci]" in commit message
# (requires GitHub plugin configuration)
```

### Multiple Webhooks
```bash
# Can have multiple webhooks pointing to same Jenkins job
# Useful for:
# - Main repository → prod builds
# - Dev repository → staging builds
# - Each webhook can have different branch filters
```

---

**✅ Webhooks are now fully configured!**

Builds will trigger automatically when you push to GitHub/GitLab/Bitbucket.
