# work in progress. Use at your own risk
import boto3
import os
import json

def get_application_id_by_name(app_name, region='us-east-1'):
    # Create a boto3 client for the AppConfig service
    appconfig_client = boto3.client('appconfig', region_name=region)

    # Initialize the paginator for the list_applications operation
    paginator = appconfig_client.get_paginator('list_applications')

    try:
        # Iterate through the pages of applications
        for page in paginator.paginate():
            print("listing applications")
            # Search each application in the current page
            for app in page['Items']:
                print("app: ", app)
                print("app name: ", app['Name'])
                if app['Name'] == app_name:
                    return app['Id']
        # If no matching application is found
        return None

    except Exception as e:
        print(f"Error occurred while searching for application ID: {e}.")
        print(f"Maybe you don't have an AppConfig application named {app_name} in {region}?")
        return None

def get_appconfig_details_by_id(application_id, environment_id, region='us-east-1'):
    # Create a boto3 client for the AppConfig service
    appconfig_client_origin = boto3.client('appconfig', region_name=region)

    try:
        # Get application details based on the application ID
        response = appconfig_client_origin.get_application(ApplicationId=application_id)

        # Extract the application name from the response
        application_name = response.get('Name', 'Unknown Application')
        
        # Get name of the environment ("Staging", "Prod", etc)
        env_response = appconfig_client_origin.get_environment(
            ApplicationId=application_id,
            EnvironmentId=environment_id
            )
        
        env_name = env_response.get('Name', 'Unknown Environment')
        
        return {'app_name': application_name, 'env_name': env_name}

    except Exception as e:
        print(f"Error occurred while retrieving application name: {e}")
        return 'Unknown Application'
        
def get_env_id(app_id, env_name, region='us-east-1'):
    # Create a boto3 client for the AppConfig service
    appconfig_client = boto3.client('appconfig', region_name=region)

    # Initialize the paginator for the list_environments operation
    paginator = appconfig_client.get_paginator('list_environments')

    try:
        # Iterate through the pages of environments
        for page in paginator.paginate(ApplicationId=app_id):
            # Search each environment in the current page
            for env in page['Items']:
                if env['Name'] == env_name:
                    return env['Id']
        # If no matching environment is found
        return None

    except Exception as e:
        print(f"Error occurred while searching for environment ID: {e}.")
        return None

def lambda_handler(event, context):
    print(event)
    # Parse the event data
    request_parameters = event['detail']['requestParameters']
    application_id = request_parameters['applicationId']
    environment_id = request_parameters['environmentId']
    configuration_profile_id = request_parameters['configurationProfileId']
    configuration_version = request_parameters['configurationVersion']
    deployment_strategy_id = request_parameters['deploymentStrategyId']
    
    # Log the extracted data
    print("Application ID:", application_id)
    print("Environment ID:", environment_id)
    print("Configuration Profile ID:", configuration_profile_id)
    print("Configuration Version:", configuration_version)
    print("Deployment Strategy ID:", deployment_strategy_id)

    # Read and log the destination region from environment variables
    target_region = os.environ['TARGET_REGION']
    print("Target Region:", target_region)
    
    names = get_appconfig_details_by_id(application_id, environment_id)
    app_name = names['app_name']
    env_name = names['env_name']
    print("App Name: ", app_name)
    print("Env Name: ", env_name)
    
    # Initialize AppConfig client for target region
    appconfig_client = boto3.client('appconfig', region_name=target_region)
    
    # Find the app ID and environment ID based on the origin region's app name and environment name
    # Make a note in the Readme that the names of these need to be unique in both regions for this to work.
    app_id = get_application_id_by_name(app_name, target_region)
    print(f"Target Application ID: {app_id}")
    
    target_env_id = get_env_id(app_id, env_name, target_region)
    print('Target Env ID: ', target_env_id)
    
    # Initialize AppConfig client for the target region
    appconfig_client = boto3.client('appconfig', region_name=target_region)

    # Deploy the configuration in the target region
    try:
        response = appconfig_client.start_deployment(
            ApplicationId=app_id,
            EnvironmentId=target_env_id,
            DeploymentStrategyId=deployment_strategy_id,
            ConfigurationProfileId=config_profile_id,
            ConfigurationVersion=config_version
        )
        print(f"Deployment initiated in {target_region}: {json.dumps(response)}")
    except Exception as e:
        print(f"Error deploying configuration: {str(e)}")

    return {
        'statusCode': 200,
        'body': json.dumps('Deployment Process Initiated')
    }

