#DigitalOcean Variables
variable "digitalocean_token" {}
variable "server_pub_key" {}
variable "server_region" { default="nyc1" }

# API Keys
variable "slack_token" {}
variable "urlscan_api_key" {}

# Whether or not to use Amazon SQS Message Queue
variable "use_sqs" { 
	type=bool
	default=false 
}

# Launch Script variables
variable "num_workers" { default="" }
variable "queue_channel" { default="" }
variable "rule_dir" { default="" }
variable "urlscan_query" { default="" }
variable "num_results" { default="" }

# Miscellaneous
variable "aws_region" { default="us-east-1" }
