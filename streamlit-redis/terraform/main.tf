# Set the required providers
terraform {
  required_providers {
    heroku = {
      source  = "heroku/heroku"
      version = "5.2.2"
    }
  }
}

# Configure the Heroku provider
provider "heroku" {
  email   = var.heroku_email_id
  api_key = var.heroku_api_key
}

# Create the Heroku app
resource "heroku_app" "my_app" {
  name   = var.app_name
  region = var.app_region
}

# Create the Heroku RedisCloud addon
resource "heroku_addon" "rediscloud" {
  app_id = heroku_app.my_app.id
  plan   = "rediscloud:30"
}