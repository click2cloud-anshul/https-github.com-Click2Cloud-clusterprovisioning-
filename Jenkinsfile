pipeline {
    environment {
        registry = "docker.io/tathagatk22/python-ex"
        registryCredential = 'docker-tathagatk22'
        dockerImage = ''
        git_url = 'https://github.com/Click2Cloud/clusterprovisioning.git'
    }
    agent any
    parameters {
		choice(
            choices: 
            [
                'branch', 
                'commit'
            ],
            description: 'Please select branch or commit to checkout from.', 
            name: 'selection'
        )
		string(
            description: 'Please insert valid input', 
            name: 'selection_value'
        )
	}
    stages {
        stage('Git checkout from Branch') {
            when {
                expression { params.selection == 'branch' }
            }
            steps {                
                git url: "$git_url", branch: "${selection_value}", credentialsId: 'git-tathagatk22' 
            }
        }
        stage('Git checkout from Commit') {
            when {
                expression { params.selection == 'commit' }
            }
            steps {
                git url: "$git_url", credentialsId: 'git-tathagat-c2c' 
                sh 'git checkout ' + "${selection_value}"
            }
        }
        // stage('Build') {
        //     steps {
        //         sh 'pip install --no-cache-dir -r requirements.txt'
        //     }
        // }
        // stage('Test') {
        //     steps {
        //         sh 'python manage.py runserver 0.0.0.0:80'
        //     }
        // }
        stage('Building image') {
            environment {
              COMMIT = sh 'echo "COMMIT=$(git rev-parse --short HEAD)"'
              BRANCH = sh 'echo "BRANCH=$(git rev-parse --abbrev-ref HEAD)"'
          }
            steps{
                script {
                    dockerImage = docker.build("$registry:$BRANCH", "--build-arg COMMIT=${COMMIT}  --build-arg BRANCH=${BRANCH} -f Dockerfile ." )
                }
            }
        }
        stage('Deploy Image') {
            steps{
                script {
                    docker.withRegistry( '', registryCredential ) {
                        dockerImage.push()
                    }
                }
            }
        }
        stage('Delete Image') {
            steps{
                sh "docker rmi $registry:$BRANCH"
            }
        }
    }
}

// dynamic fetching of git branches using credentials
// import jenkins.model.*

// credentialsId = 'git-tathagatk22'

// def creds = com.cloudbees.plugins.credentials.CredentialsProvider.lookupCredentials(
//   com.cloudbees.plugins.credentials.common.StandardUsernameCredentials.class, Jenkins.instance, null, null ).find{
//     it.id == credentialsId}

// def gettags = ("git ls-remote -t -h https://"+creds.username+":"+creds.password+"@github.com/tathagatk22/nodejs-ex.git").execute()
// return gettags.text.readLines().collect { 
//   it.split()[1].replaceAll('refs/heads/', '').replaceAll('refs/tags/', '').replaceAll("\\^\\{\\}", '')
// }
