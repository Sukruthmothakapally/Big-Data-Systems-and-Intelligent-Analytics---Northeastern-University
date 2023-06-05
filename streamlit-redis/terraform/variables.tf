variable "heroku_email_id" {
  description = "Your email address is your identity on Heroku and is used to log in."
  type        = string
}

variable "heroku_api_key" {
  description = "Heroku API key"
  type        = string
}

variable "app_name" {
  description = "Heroku app name"
  type        = string
}

variable "app_region" {
  description = "Heroku App region to be deployed in US or Europe"
  type        = string
  default     = "us"
}