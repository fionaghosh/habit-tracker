pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "fionaghosh/habit-tracker:${env.BUILD_NUMBER}"
        REGISTRY     = "docker.io"
        APP_NAME     = "habit-tracker"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
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
                bat "docker run --rm %DOCKER_IMAGE% flake8 . --exit-zero > flake-report.txt"
                archiveArtifacts artifacts: 'flake-report.txt', fingerprint: true
            }
        }

        stage('Security Scan') {
            steps {
                bat 'docker run --rm -v "%WORKSPACE%":/app -w /app %DOCKER_IMAGE% bandit -r . -f html -o bandit-report.html --exit-zero'
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
                bat "docker rm -f %APP_NAME% || echo ignored"
                bat "docker run -d --name %APP_NAME% -p 8000:8000 %REGISTRY%/%DOCKER_IMAGE%"
            }
        }

        stage('Monitoring') {
            steps {
                // 1) Health check
                bat 'curl -sf http://localhost:8000/healthz || exit 1'

                // 2) Metrics snapshot
                bat 'curl http://localhost:8000/metrics > metrics_snapshot.txt'

                // 3) Archive
                archiveArtifacts artifacts: 'metrics_snapshot.txt', fingerprint: true
            }
        }
    }  // end stages

    post {
        success {
            echo "🎉 Build ${env.BUILD_NUMBER} succeeded!"
        }
        failure {
            echo "❌ Build ${env.BUILD_NUMBER} failed."
        }
    }
}  // end pipeline

