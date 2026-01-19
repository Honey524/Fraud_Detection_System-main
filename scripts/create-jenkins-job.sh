#!/bin/bash
# Jenkins Pipeline Job Creator
# This script helps create the Fraud Detection CI/CD Pipeline in Jenkins

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║       Creating Jenkins Pipeline Job via CLI                       ║"
echo "╚════════════════════════════════════════════════════════════════════╝"

JENKINS_URL="http://localhost:8080"
JENKINS_USER="admin"
JENKINS_PASSWORD="e25518d82fde4149932643f468b521e1"
JOB_NAME="fraud-detection-pipeline"

# Create job configuration XML
cat > /tmp/jenkins-job-config.xml << 'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.40">
  <description>Fraud Detection System CI/CD Pipeline - Automated build, test, and deployment</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <hudson.model.BooleanParameterDefinition>
          <name>PUSH_IMAGES</name>
          <description>Push Docker images to registry after build</description>
          <defaultValue>false</defaultValue>
        </hudson.model.BooleanParameterDefinition>
        <hudson.model.StringParameterDefinition>
          <name>REGISTRY</name>
          <description>Docker registry URL</description>
          <defaultValue>docker.io/yourusername</defaultValue>
        </hudson.model.StringParameterDefinition>
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.90">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@4.10.0">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>file:///var/jenkins_home/workspace/fraud-detection-pipeline</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="list"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF

echo ""
echo "📝 Job configuration created at: /tmp/jenkins-job-config.xml"
echo ""
echo "🔧 Creating Jenkins job via CLI..."

# Create the job using Jenkins CLI
curl -s -X POST "${JENKINS_URL}/createItem?name=${JOB_NAME}" \
  --user "${JENKINS_USER}:${JENKINS_PASSWORD}" \
  --header "Content-Type: application/xml" \
  --data-binary @/tmp/jenkins-job-config.xml

if [ $? -eq 0 ]; then
  echo "✅ Job '${JOB_NAME}' created successfully!"
else
  echo "⚠️  Job may already exist or there was an error. Check Jenkins UI."
fi

echo ""
echo "🎯 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Visit: ${JENKINS_URL}/job/${JOB_NAME}"
echo "2. Click 'Build with Parameters'"
echo "3. Configure parameters (optional):"
echo "   - PUSH_IMAGES: false (set to true to push to registry)"
echo "   - REGISTRY: docker.io/yourusername"
echo "4. Click 'Build' to start the pipeline"
echo ""
echo "📊 Pipeline will execute the following stages:"
echo "   ✓ Checkout code"
echo "   ✓ Run tests"
echo "   ✓ Lint & security checks"
echo "   ✓ Build Docker images"
echo "   ✓ Start services"
echo "   ✓ Health checks"
echo "   ✓ Deploy with Ansible"
echo ""
echo "🌐 Access Jenkins: ${JENKINS_URL}"
echo "🔑 Username: ${JENKINS_USER}"
echo ""

# Clean up
rm -f /tmp/jenkins-job-config.xml
