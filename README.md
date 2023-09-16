# AWS Infrastructure Deployment.
This stack uses Severless Framework, Makefile, Python, Selenium, Deadless Chronium, AWS and circleci to deployment infrustracture which is capable to deploying hundreds of lambdas to scrap information, process information, and store information.


### Usage
```
make deploy
curl -i -H "x-api-key: xxxxxxxxxxxxxxxxxxxxxxxx" https://xxxxxxxxx.execute-api.us-west-2.amazonaws.com/beta/V1/RM\?dropID\=xxxx
```

_default sls deploy will deploy to aws lab account as beta_

_sls deploy --env lab/preprod/prod --stage beta_

#### A secretes file is required run above commands.
```config/secrets-labs.env```

```
export AWS_ACCESS_KEY_ID=xxxxxxxxxxxxxxxxxxxxxxxx
export AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
export AWS_DEFAULT_REGION=xxxxxxxxxxxxxxxxxxxxxxxx
```


#### Further, environment variable files are required for lambda execuction
```
config/env-var/aws-labs.json
config/env-var/aws-s3-legacy-access.json
```

```
aws-labs.json
{
    "aws_access_key_id": "xxxxxxxxxxxxxxxxxxxxx",
    "aws_secret_access_key": "xxxxxxxxxxxxxxxxxxxxx",
    "aws_region": "xxxxxxxxxxxxxxxxxxxxx"
}

aws-s3-legacy-access.json
{
    "aws_access_key_id":"xxxxxxxxxxxxxxxxxxxxx",
    "aws_secret_access_key":"xxxxxxxxxxxxxxxxxxxxx
}
```


### What this project does
_This code allows users to request an API Gateway GET endpoint with a file id and determine if the mail file is passing or failing based off global & unique campaign settings._


![c4 container](./docs/deployment.svg)
