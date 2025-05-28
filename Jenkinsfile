pipeline {
  agent any

  environment {
    DOCKER_IMAGE      = "fionaghosh/habit-tracker:${env.BUILD_NUMBER}"
    REGISTRY          = "docker.io"
    APP_NAME          = "habit-tracker"

    SONAR_PROJECT_KEY = "fionaghosh_habit-tracker"
    SONAR_ORGANIZATION= "fionaghosh"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build') {
      steps {
        // 1) Build your Docker image
        bat "docker build -t %DOCKER_IMAGE% ."
        // 2) Save the image ID so we can fingerprint it
        bat "docker inspect --format=\"{{.Id}}\" %DOCKER_IMAGE% > image-id.txt"
        archiveArtifacts artifacts: 'image-id.txt', fingerprint: true
      }
    }

    stage('Test') {
      steps {
        bat "docker run --rm %DOCKER_IMAGE% pytest -q tests"
      }
    }

    stage('Code Quality') {
  steps {
    withSonarQubeEnv('SonarCloud') {
      script {
        def scannerHome = tool name: 'DefaultScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
        bat """
          \"${scannerHome}\\bin\\sonar-scanner.bat\" ^
            -Dsonar.host.url=%SONAR_HOST_URL% ^
            -Dsonar.login=%SONAR_AUTH_TOKEN% ^
            -Dsonar.organization=%SONAR_ORGANIZATION% ^
            -Dsonar.projectKey=%SONAR_PROJECT_KEY% ^
            -Dsonar.sources=.
        """
      }
    }
  }
}





stage('Security Scan') {
  steps {
    script {
      // pull in the Dependency-Check installation you configured under Global Tool Configuration
      // (replace 'DependencyCheck' with the exact name you gave it)
      def dcHome = tool name: 'DependencyCheck', type: 'org.jenkinsci.plugins.DependencyCheck.DependencyCheckInstallation'

      // run the bundled CLI from that home
      bat """
        \"${dcHome}\\bin\\dependency-check.bat\" ^
          --project habit-tracker ^
          --scan . ^
          --out reports\\\\security
      """
    }

    // archive whatever got produced (won’t fail if it’s empty)
    archiveArtifacts artifacts: 'reports/security/**', allowEmptyArchive: true, fingerprint: true
  }

  post {
    always {
      echo "✅ Security scan completed (reports archived)"
    }
  }
}


    stage('Deploy to Staging') {
      steps {
        bat """
          docker rm -f staging-%APP_NAME% || echo ignored
          docker run -d --name staging-%APP_NAME% -p 5000:5000 %DOCKER_IMAGE%
        """
      }
    }

    stage('Release to Production') {
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub-creds',
          usernameVariable: 'DOCKERHUB_USER',
          passwordVariable: 'DOCKERHUB_PASS'
        )]) {
          bat "docker login -u %DOCKERHUB_USER% -p %DOCKERHUB_PASS% %REGISTRY%"
          bat "docker tag %DOCKER_IMAGE% %REGISTRY%/%DOCKER_IMAGE%"
          bat "docker push %REGISTRY%/%DOCKER_IMAGE%"
        }
        bat """
          ssh deploy@production-server ^
            "docker pull %REGISTRY%/%DOCKER_IMAGE% &&
             docker rm -f prod-%APP_NAME% || true &&
             docker run -d --name prod-%APP_NAME% -p 80:5000 %REGISTRY%/%DOCKER_IMAGE%"
        """
      }
    }

    stage('Monitoring & Alerting') {
      steps {
        // Health check
        bat 'curl -sf http://production-server/healthz || exit 1'
        // Metrics snapshot
        bat 'curl http://production-server/metrics > metrics_snapshot.txt'
        archiveArtifacts artifacts: 'metrics_snapshot.txt', fingerprint: true
        // (You could trigger alerts here via a CLI to Datadog/New Relic, etc.)
      }
    }
  }

  post {
    success { echo "✅ Pipeline #${env.BUILD_NUMBER} succeeded!" }
    failure { echo "❌ Pipeline #${env.BUILD_NUMBER} failed!" }
  }
}

