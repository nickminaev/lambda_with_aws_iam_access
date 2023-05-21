This repository is a follow up tutorial for [this amazing post](https://itnext.io/creating-an-https-lambda-endpoint-without-api-gateway-eb0db1f6af7a).

# Prerequisites
- An AWS account.
- AWS credentials configured, so you can deploy the resources described in the `main.tf` file.
- Python 3 installed on your device.
- Hashicorp’s Terraform installed.
- Having read Shane’s article and implemented it.
- Basic familiriaty with the concepts of AWS users and IAM.
- Note that I’ve simplified the deployment of the function. My sample lambda_handler does not require any dependencies.So, I just zipped the file containing it (i.e. lambda_functino.py) into the package.zip archive.

# Additional info

Additional info can be found in [blog](https://www.nickminaev.com/posts/tf-aws-lambda-url-with-auth.html).

# But my hands are itching

Run the following commands and you'll see the demonstration in its full swing!

```bash
terraform init
./deploy.sh
pip3 install -r requirements.txt
python3 demonstrate_secure_lambda_invocation.py
```




