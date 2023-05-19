This repository is a follow up tutorial for [this amazing post](https://itnext.io/creating-an-https-lambda-endpoint-without-api-gateway-eb0db1f6af7a).

As opposed to Shane, I did the following things:
- Simplified the deployment of the function. This was done for the sake of simplicity.
- Added the `AWS_IAM` to the function's URL, so only authorized calls are accepted.
- Added some additional resources in the `main.tf` file to make it possible.
- In the `demonstrate_request.py` I'm showing the whole pipeline of getting the credentials for the user,
  getting temporary ones via assuming the role and finally invoking the lambda with the highly popular `requests`
  Python library.

Prerequisites:
- An AWS account.
- AWS credentials configured, so you can deploy the resources described in the `main.tf` file.
- Python 3 installed on your device.
- Hashicorp's Terraform installed.

Run the following commands and you'll see the demonstration in its full swing!

```bash
terraform init
terraform apply
pip3 install -r requirements.txt
python3 demonstrate_secure_lambda_invocation.py
```

A blog post on [my blog](www.nickminaev.com) is yet to be published. Stay tuned.


