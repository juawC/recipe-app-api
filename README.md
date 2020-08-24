# Zappa configuration

### Add ~/.aws/credentials file
	[default]
	aws_access_key_id= XXXXXXXXXXXXXXXXXXXX
	aws_secret_access_key=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
	
### Add aws.env file to the root of the prject
This file should be copied from `aws.env.example`

	AWS_ACCESS_KEY_ID=key
	AWS_SECRET_ACCESS_KEY=key
	DB_HOST=host
	DB_NAME=name
	DB_USER=user
	DB_PASS=pass
	DB_PORT=3306
	S3_BUCKET=api-recipe-test-9123123
	AWS_SG=sg-xxxxx
	SUBNET_ID_1=subnet-xxxxx
	SUBNET_ID_2=subnet-xxxxx
	SUBNET_ID_3=subnet-xxxxx
	
## How to use Zappa
1. Run docker compose comand:
`docker-compose -f docker-compose-zappa.yml run --rm django /bin/bash`
2. Run command to generate zappa_seetings.json from template:
`./generate_zappa_settings.sh `
3. Activate venv inside container:
`source /venv/bin/activate`
4. Install your requirements.txt to your virtual environment: (You only need to do this when requirements.txt is changed)
`pip install -r requirements/requirements.txt`

### Deploy/Update
Run zappa deploy command, if it is not deployed yet, otherwise run zappa update command instead:
`zappa deploy dev`
`zappa update dev`

### Serving Static Files
1. Enable CORS for the S3 bucket that you are using:

		 <CORSConfiguration>
	        <CORSRule>
	            <AllowedOrigin>*</AllowedOrigin>
	            <AllowedMethod>GET</AllowedMethod>
	            <MaxAgeSeconds>3000</MaxAgeSeconds>
	            <AllowedHeader>Authorization</AllowedHeader>
	        </CORSRule>
		</CORSConfiguration>
2. Push the static files to the cloud:
`python manage.py collectstatic --noinput`
3. Update:
`zappa update dev`

### Setup Serverless MySQL Database
1. Create an MySQL Aurora serverless cluster.
2. Configure Virtual Private Cloud (VPC) and Security Groups.
3. Create db in MySQL Aurora serverless cluster:
`zappa manage dev create_db`
4. Migrate DB:
`zappa manage dev migrate`
5. Create admin user:
`zappa invoke --raw dev "from core.models import User; User.objects.create_superuser('youruser', 'yourpassword')"
`

	