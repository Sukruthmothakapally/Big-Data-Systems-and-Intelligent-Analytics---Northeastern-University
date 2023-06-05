## Deploy using Terraform

### Steps

1. Install Terraform binary - [downloads](https://developer.hashicorp.com/terraform/downloads)
2. Create an account on Heroku and add billing information
3. From the account setting copy the following secrets
    * Email id
    * API Key
4. Update the [tfvar file](./example_terraform.tfvars)
    ```
    heroku_email_id="some@email.com"
    heroku_api_key="qwerty12345apikey"
    app_name="streamlit-redis"
    app_region="us"
    ```
5. Rename the file from `example_terraform.tfvars` to `terraform.tfvars`
6. Initialize  Terraform
    ```bash
    terraform init
    ```
7. Terraform Plan
    ```bash
    terraform plan
    ```
8. Terraform Apply
    ```bash
    terraform apply --auto-approve
    ```
    The following files on local allows terraform to track the state of the remote resources, so do not delete or manually edit these
    * terraform.tfstate
    * terraform.tfstate.backup

9. Terraform Destroy (After end of app lifecycle)
    ```bash
    terraform destroy --auto-approve
    ```