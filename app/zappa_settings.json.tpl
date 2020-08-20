{
    "dev": {
        "django_settings": "app.settings",
        "profile_name": "default",
        "project_name": "recipe-app-api",
        "runtime": "python3.8",
        "s3_bucket": "$S3_BUCKET",
        "aws_region": "eu-west-2",
        "environment_variables": {
            "DB_HOST": "$DB_HOST",
            "DB_NAME": "$DB_NAME",
            "DB_USER": "$DB_USER",
            "DB_PASS": "$DB_PASS",
            "DB_PORT": "$DB_PORT",
            "USE_AWS": "True"
        },
        "vpc_config" : {
            "SubnetIds": [ "$SUBNET_ID_1", "$SUBNET_ID_2", "$SUBNET_ID_3" ],
            "SecurityGroupIds": [ "$AWS_SG" ]
        }
    }
}