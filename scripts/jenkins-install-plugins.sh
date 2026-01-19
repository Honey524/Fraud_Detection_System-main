#!/bin/bash
# Jenkins Plugin Installation Script
# Installs essential plugins for Fraud Detection CI/CD pipeline

set -e

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_HOME="${JENKINS_HOME:-.}/jenkins_home"
PLUGINS_DIR="$JENKINS_HOME/plugins"

echo "🔧 Installing Jenkins plugins..."

# Create plugins directory if it doesn't exist
mkdir -p "$PLUGINS_DIR"

# List of essential plugins with versions
PLUGINS=(
    "workflow-aggregator:596.v8c21c963d92d"           # Pipeline
    "pipeline-stage-view:2.28"                         # Stage View
    "git:5.0.1"                                        # Git
    "credentials-binding:1.28"                         # Credentials Binding
    "timestamper:1.18"                                 # Timestamper
    "docker-commons:1.21"                              # Docker Commons
    "docker-workflow:1.31"                             # Docker Pipeline
    "github:1.37.2"                                    # GitHub Integration
    "ansicolor:1.0.1"                                  # AnsiColor
    "log-parser:2.2"                                   # Log Parser
    "email-ext:2.97"                                   # Email Extension
    "slack:700.v5de25e5cd681"                          # Slack Notification
    "jira:3.10.2"                                      # JIRA Integration
    "performance:3.20"                                 # Performance Plugin
    "warnings-ng:11.1.2"                               # Warnings Next Generation
    "owasp-dependency-check:5.4.3"                     # OWASP Dependency Check
    "sonarqube-generic-coverage:1.3"                   # SonarQube
)

# Function to download plugin
download_plugin() {
    local plugin=$1
    local plugin_name="${plugin%:*}"
    local plugin_version="${plugin#*:}"
    
    echo "⬇️  Downloading $plugin_name version $plugin_version..."
    
    if [ ! -f "$PLUGINS_DIR/$plugin_name.hpi" ]; then
        curl -L -o "$PLUGINS_DIR/$plugin_name.hpi" \
            "https://updates.jenkins.io/download/plugins/$plugin_name/$plugin_version/$plugin_name.hpi" \
            2>/dev/null || echo "⚠️  Failed to download $plugin_name (might be normal if not available)"
    else
        echo "✅ $plugin_name already installed"
    fi
}

# Download all plugins
for plugin in "${PLUGINS[@]}"; do
    download_plugin "$plugin"
done

echo ""
echo "✅ Plugin download complete!"
echo "📝 Next steps:"
echo "   1. Restart Jenkins: docker restart jenkins"
echo "   2. Jenkins will install plugins on startup"
echo "   3. Wait ~5 minutes for all plugins to initialize"
echo "   4. Go to http://localhost:8080/pluginManager/installed to verify"
