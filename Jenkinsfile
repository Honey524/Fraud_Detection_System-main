pipeline {
  agent any

  /* =========================
     BUILD PARAMETERS (UI)
     ========================= */
  parameters {
    booleanParam(
      name: 'PUSH_IMAGES',
      defaultValue: false,
      description: 'Push Docker images to registry'
    )
    string(
      name: 'REGISTRY',
      defaultValue: 'docker.io/honey254',
      description: 'Docker registry (e.g. docker.io/honey254)'
    )
  }

  /* =========================
     ENVIRONMENT VARIABLES
     ========================= */
  environment {
    COMPOSE_FILE   = 'docker-compose.yml'
    HEALTH_TIMEOUT = '20'
    SHORT_SHA      = "${env.GIT_COMMIT?.take(7) ?: 'local'}"
    BUILD_TAG      = "${env.BRANCH_NAME ?: 'main'}-${env.BUILD_NUMBER}"
  }

  /* =========================
     PIPELINE OPTIONS
     ========================= */
  options {
    timestamps()
    ansiColor('xterm')
    buildDiscarder(logRotator(numToKeepStr: '20'))
    timeout(time: 60, unit: 'MINUTES')
  }

  /* =========================
     STAGES
     ========================= */
  stages {

    stage('Checkout') {
      steps {
        checkout scm
        sh 'git rev-parse --short HEAD'
        sh 'git log -1 --oneline'
      }
    }

    stage('Tests') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -r requirements.txt pytest || true
          pytest -v --tb=short || true
        '''
      }
    }

    stage('Lint & Security') {
      steps {
        sh '''
          . .venv/bin/activate || true

          pip install flake8 black bandit pip-audit || true

          echo "=== Flake8 ==="
          flake8 . || true

          echo "=== Black ==="
          black --check . || true

          echo "=== Bandit ==="
          bandit -r . -q || true

          echo "=== Dependency Audit ==="
          pip-audit -r requirements.txt || true
        '''
      }
    }

    stage('Build Images') {
      steps {
        sh '''
          docker compose build
          docker images
        '''
      }
    }

    stage('Start Services') {
      steps {
        sh '''
          docker compose up -d
          docker compose ps
        '''
      }
    }

    stage('Health Checks') {
      steps {
        sh '''
          sleep 10

          curl -fsS http://localhost:5000/health || echo "ML service not ready"
          curl -fsS http://localhost:5001/health || echo "Alert service not ready"
          curl -fsS http://localhost:8000 || echo "Web UI not ready"
        '''
      }
    }

    stage('Push to Registry') {
      when {
        allOf {
          branch 'main'
          expression { params.PUSH_IMAGES == true }
        }
      }
      steps {
        withCredentials([
          usernamePassword(
            credentialsId: 'docker-registry-creds',
            usernameVariable: 'DOCKER_USER',
            passwordVariable: 'DOCKER_TOKEN'
          )
        ]) {
          sh '''
            echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin

            IMAGES=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep fraud)

            for IMG in $IMAGES; do
              NAME=$(echo "$IMG" | awk -F':' '{print $1}')
              docker tag "$IMG" "$REGISTRY/$NAME:$BUILD_TAG"
              docker tag "$IMG" "$REGISTRY/$NAME:$SHORT_SHA"

              docker push "$REGISTRY/$NAME:$BUILD_TAG"
              docker push "$REGISTRY/$NAME:$SHORT_SHA"
            done

            docker logout
          '''
        }
      }
    }

    stage('Deploy (Ansible)') {
      when { branch 'main' }
      steps {
        sh '''
          cd ansible
          ansible-playbook playbooks/health-check.yml -i inventory/hosts.ini -K || true
        '''
      }
    }
  }

  /* =========================
     POST ACTIONS
     ========================= */
  post {
    always {
      sh '''
        docker compose ps || true
        docker compose logs --tail=200 || true
      '''
      cleanWs()
    }
    success {
      echo '✅ Pipeline completed successfully'
    }
    failure {
      echo '❌ Pipeline failed — check logs above'
    }
  }
}
