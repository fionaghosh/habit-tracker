pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "fionaghosh/habit-tracker:${env.BUILD_NUMBER}"
        REGISTRY     = "docker.io"
        APP_NAME     = "habit-tracker"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Build') {
            steps {
                // Inside bat, use %DOCKER_IMAGE% not ${DOCKER_IMAGE}
                bat "docker build -t %DOCKER_IMAGE% ."
            }
        }

        stage('Test') {
            steps {
                bat "docker run --rm %DOCKER_IMAGE% pytest -q tests"
            }
        }

        stage('Code Quality') {
    steps {
        // Run flake8, report warnings but don’t fail the build
        bat "docker run --rm %DOCKER_IMAGE% flake8 . --exit-zero > flake-report.txt"

        // Archive the flake8 text report
        archiveArtifacts artifacts: 'flake-report.txt', fingerprint: true
    }
}



        stage('Security Scan') {
    steps {
        // Run Bandit, produce HTML report, but don’t fail the build on issues
        bat "docker run --rm %DOCKER_IMAGE% bandit -r . -f html -o bandit-report.html --exit-zero"

        // Archive the Bandit report for review
        archiveArtifacts artifacts: 'bandit-report.html', fingerprint: true
    }
}


        stage('Release') {
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
            }
        }

        stage('Deploy') {
            steps {
                // If SSH is available on your Windows node
                bat """
                  ssh deploy@your-server ^
                    "docker pull %REGISTRY%/%DOCKER_IMAGE% && ^
                     docker rm -f %APP_NAME% || echo ignored && ^
                     docker run -d --name %APP_NAME% -p 8000:8000 %REGISTRY%/%DOCKER_IMAGE%"
                """
            }
        }

        stage('Monitoring') {
            steps {
                bat "curl -sf http://your-server:8000/healthz || exit 1"
                bat "curl http://your-server:8000/metrics > metrics_snapshot.txt"
                archiveArtifacts artifacts: 'metrics_snapshot.txt', fingerprint: true
            }
        }
    }

    post {
        success { echo "🎉 Build ${env.BUILD_NUMBER} succeeded!" }
        failure { echo "❌ Build ${env.BUILD_NUMBER} failed." }
    }
}
