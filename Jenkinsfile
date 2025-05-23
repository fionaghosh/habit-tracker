pipeline {
  agent any

  environment {
    // adjust these to your own values
    DOCKER_IMAGE = "fionaghosh/habit-tracker:${env.BUILD_NUMBER}"
    REGISTRY     = "docker.io"
    APP_NAME     = "habit-tracker"
  }

  stages {
    /*───────────────────────────────────────────────────────────────────*/
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    /*───────────────────────────────────────────────────────────────────*/
    stage('Build') {
      steps {
        // 1) Build your artifact; here we build a Docker image
        sh 'docker build -t $DOCKER_IMAGE .'
        // 2) Archive the image ID (optional) or push as a build artifact
        sh 'docker inspect --format="{{.Id}}" $DOCKER_IMAGE > image-id.txt'
        archiveArtifacts artifacts: 'image-id.txt', fingerprint: true
      }
    }

    /*───────────────────────────────────────────────────────────────────*/
    stage('Test') {
      steps {
        // Run your automated tests in the container
        sh 'docker run --rm $DOCKER_IMAGE pytest -q tests'
      }
    }

    /*───────────────────────────────────────────────────────────────────*/
    stage('Code Quality') {
      steps {
        // Example: SonarQube scanner (requires Sonar plugin & configuration)
        withSonarQubeEnv('MySonarQubeServer') {
          sh 'sonar-scanner -Dsonar.projectKey=habit-tracker'
        }
      }
    }

    /*───────────────────────────────────────────────────────────────────*/
    stage('Security Scan') {
      steps {
        // Example: run OWASP Dependency-Check
        sh 'dependency-check.sh --project habit-tracker --scan . --out reports/security'
        archiveArtifacts artifacts: 'reports/security/**', fingerprint: true
      }
      post {
        always {
          // parse and show summary, or fail-on-high-severity
          // you can hook in Jenkins Dependency-Check plugin here
        }
      }
    }

    /*───────────────────────────────────────────────────────────────────*/
    stage('Deploy to Staging') {
      steps {
        // Deploy your built artifact to a staging/test environment
        // Example: pull & run via Docker
        sh '''
          docker rm -f staging-${APP_NAME} || true
          docker run -d --name staging-${APP_NAME} -p 5000:5000 $DOCKER_IMAGE
        '''
      }
    }

    /*───────────────────────────────────────────────────────────────────*/
    stage('Release to Production') {
      steps {
        // Promote the same image into production
        // Example: push to Docker Hub, then SSH + docker pull on prod
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',
          usernameVariable: 'DOCKERHUB_USER',
          passwordVariable: 'DOCKERHUB_PASS'
        )]) {
          sh 'docker login -u $DOCKERHUB_USER -p $DOCKERHUB_PASS $REGISTRY'
          sh 'docker tag $DOCKER_IMAGE $REGISTRY/$DOCKER_IMAGE'
          sh 'docker push $REGISTRY/$DOCKER_IMAGE'
        }
        // Then deploy remotely
        sh '''
          ssh deploy@production-server '
            docker pull $REGISTRY/$DOCKER_IMAGE &&
            docker rm -f prod-${APP_NAME} || true &&
            docker run -d --name prod-${APP_NAME} -p 80:5000 $REGISTRY/$DOCKER_IMAGE
          '
        '''
      }
    }

    /*───────────────────────────────────────────────────────────────────*/
    stage('Monitoring & Alerting') {
      steps {
        // Example: hit a health endpoint
        sh 'curl -sf http://production-server/healthz || exit 1'

        // Example: snapshot metrics
        sh 'curl http://production-server/metrics > metrics_snapshot.txt'
        archiveArtifacts artifacts: 'metrics_snapshot.txt', fingerprint: true

        // You could also fire an alert or integrate with Datadog/New Relic here
      }
    }
  }

  post {
    success { echo "✅ Pipeline #${env.BUILD_NUMBER} succeeded!" }
    failure { echo "❌ Pipeline #${env.BUILD_NUMBER} failed!" }
  }
}

