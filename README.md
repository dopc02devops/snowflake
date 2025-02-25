
# Airbyte Local Installation Guide

This guide will walk you through the steps to install and manage Airbyte locally on your machine using the `abctl` command-line tool.

## Prerequisites
Before starting, ensure you have the following installed on your machine:
- **Homebrew**: A package manager for macOS and Linux.
- **Docker**: Airbyte requires Docker to run the services.

## Step 1: Download Airbyte
To begin, install the `abctl` command-line tool using Homebrew:
```bash
brew tap airbytehq/tap
brew install abctl
brew upgrade abctl
```
## Step 2: Install Airbyte Locally
Once abctl is installed, you can install Airbyte locally. There are several installation options based on your requirements:

- Basic installation (default):
```bash
abctl local install --insecure-cookies
```
- Low-resource mode (for machines with limited resources):
```bash
abctl local install --low-resource-mode
```
- Low-resource mode with insecure cookies (for machines with limited resources and if you need insecure cookies enabled):
```bash
abctl local install --low-resource-mode --insecure-cookies
```
## Step 3: Set Up Credentials
To set up your Airbyte local credentials, run the following command:
```bash
abctl local credentials
```
This will prompt you to enter the required credentials for the Airbyte instance.

## Step 4: Change Password
To change the password for your local Airbyte instance, run the following command:
```bash
abctl local credentials --password YourStrongPasswordExample
```
Replace YourStrongPasswordExample with your new password.

## Step 5: Uninstall Airbyte
If you ever need to uninstall Airbyte, you can do so with the following command:
- Uninstall Airbyte (but keep persisted data):
```bash
abctl local uninstall
```
- Completely uninstall Airbyte (including persisted data):
```bash
abctl local uninstall --persisted
```
- Remove any leftover configuration files:
```bash
rm -rf ~/.airbyte/abctl
```
This will remove all configurations and cached data related to Airbyte from your system.

## links
- https://docs.airbyte.com/using-airbyte/getting-started/oss-quickstart
- https://clickhouse.com/docs/knowledgebase/how-to-set-up-ch-on-docker-odbc-connect-mssql

### EMAIL
USER_EMAIL=dopc02devops1@gmail.com
ORGANISATION: NSN

## Docker commands
docker-compose up --build -d
docker-compose up -d --force-recreate
docker-compose down