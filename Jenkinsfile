pipeline {
    agent {
        docker {
            image 'debian:9'
            label 'debian stretch'
        }
    }

    stages {
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
    }
}
