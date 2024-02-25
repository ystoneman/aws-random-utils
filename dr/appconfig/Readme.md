# README - Amazon AppConfig Feature Flag Replication Lambda

## Overview

This AWS Lambda function is designed to respond to feature flag updates in a primary (origin) AWS region and replicate these changes to a designated disaster recovery (DR) region. It's useful for maintaining feature flag consistency across different AWS regions.

### Disclaimer

This code is provided for educational and inspirational purposes only. It is not intended for production use. Before deploying this solution in a production environment, thorough testing and validation are required. Additionally, it is crucial to tailor the code and IAM policies to the specific needs of your environment to ensure security and efficiency.

## Functionality

The Lambda function triggers on specific AppConfig events in the origin region. It then replicates the relevant configuration changes to the AppConfig service in the DR region.

## Pre-requisites

- AWS Lambda function with access to AppConfig APIs in both the origin and DR regions.
- Properly configured IAM roles and permissions.
- Environment variables set for the Lambda function.
- Set the timeout to 30 seconds, because with the default Memory, it can take just over 3 seconds long.
- Event pattern based rule in Amazon EventBridge.
- Applications and environments should already be created in the DR region. They must have the same names as in the origin region for the replication to work correctly.

## IAM Permissions

The Lambda function requires permissions to interact with AppConfig APIs in both the origin and DR regions. 

**Sample IAM Policy Statement:**

```json
{
    "Effect": "Allow",
    "Action": [
        "appconfig:*"
    ],
    "Resource": [
        "*"
    ]
}
```

**Note**: The above policy is more permissive than necessary. It should be narrowed down to follow the principle of least privilege.

## Environment Variables
Set environment variables for the Lambda function to define the DR region.

**Example:**

- Key: `TARGET_REGION`
- Value: `us-west-2` (if your main region is `us-east-1` and your DR region is `us-west-2`)

## EventBridge Configuration
Configure an Event pattern-based rule in Amazon EventBridge to trigger the Lambda function.

**Sample Event Pattern:**

```json
{
  "source": ["aws.appconfig"],
  "region": ["us-east-1"],
  "detail": {
    "eventName": ["StartDeployment"]
  }
}
```

**Note**: Replace the region with your origin region. This configuration helps avoid an endless loop by triggering the automation only for events in the specified region.

## Additional Considerations
- **Unique Naming**: The names of applications and environments should be consistent across regions for this code to work, as it matches these names across regions. Ensure that these names are unique within each region but identical across the origin and DR regions to facilitate proper replication.
- **Rollback Scenarios**: Currently, this Lambda function covers only the start of deployments. Rollback scenario support is a planned future enhancement.
- **Testing**: Test the function thoroughly in a non-production environment to ensure it behaves as expected.
- **Monitoring**: Set up monitoring and alerting for the Lambda function to track its performance and catch any issues early.
- **Consolidating**: Instantiate an origin region client once and a target region client once, and then pass those into function as parameters.
- **Versioning**: The version numbers supported are currently only the immutable `LatestVersionNumber` (integer), rather than the more human `VersionLabel` (string -- for example, “v2.2.0”). But you can modify the code to support that.

## Conclusion
This Lambda function serves as a sample foundational tool snippet for replicating AppConfig feature flags across regions. Remember, customization and thorough testing are key to successfully implementing this solution in a real-world environment.
