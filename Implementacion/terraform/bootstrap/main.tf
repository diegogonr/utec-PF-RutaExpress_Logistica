terraform {
  required_version = ">= 1.6.0"
  required_providers {
    azurerm = { source = "hashicorp/azurerm", version = "~> 3.110" }
    aws     = { source = "hashicorp/aws", version = "~> 5.60" }
    google  = { source = "hashicorp/google", version = "~> 5.40" }
    random  = { source = "hashicorp/random", version = "~> 3.6" }
  }
}

provider "azurerm" {
  features {}
}

provider "aws" {
  region = var.aws_region
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

resource "random_string" "suffix" {
  length  = 6
  special = false
  upper   = false
}

# --- Azure state ---
resource "azurerm_resource_group" "tfstate" {
  name     = var.azure_tfstate_rg
  location = var.azure_region
  tags     = var.tags
}

resource "azurerm_storage_account" "tfstate" {
  name                     = var.azure_storage_account_name
  resource_group_name      = azurerm_resource_group.tfstate.name
  location                 = azurerm_resource_group.tfstate.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

resource "azurerm_storage_container" "tfstate" {
  name                  = "tfstate"
  storage_account_name  = azurerm_storage_account.tfstate.name
  container_access_type = "private"
}

# --- AWS state ---
resource "aws_s3_bucket" "tfstate" {
  bucket = var.aws_tfstate_bucket
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_dynamodb_table" "tfstate_lock" {
  name         = var.aws_tfstate_lock_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  tags         = var.tags

  attribute {
    name = "LockID"
    type = "S"
  }
}

# --- GCP state ---
resource "google_storage_bucket" "tfstate" {
  name                        = var.gcp_tfstate_bucket
  location                    = var.gcp_region
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
  labels = var.tags
}
