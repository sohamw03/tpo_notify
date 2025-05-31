# TPO Notify

An automated notification system for Training and Placement Office (TPO) portal that monitors and alerts about new opportunities.

## Features

- Automated login to TPO portal
- Monitors for new placement/internship opportunities
- Email notifications for new opportunities
- MongoDB integration for tracking notifications
- Configurable settings via environment variables

## Tech Stack

- [Python](https://www.python.org/) 3.11+
- [Selenium WebDriver](https://www.selenium.dev/documentation/webdriver/)
- [MongoDB](https://www.mongodb.com/)
- [Resend](https://resend.com/) (for email notifications)
- [UV](https://docs.astral.sh/uv/) (dependency management)

## Prerequisites

1. Install [Python 3.11](https://www.python.org/downloads/) or higher
2. Install [UV]
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   exec bash
   uv sync
   ```
3. Install [Chrome browser](https://www.google.com/chrome/)
4. Create accounts on:
   - [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
   - [Resend](https://resend.com/signup)

## Installation

1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies using Poetry
4. Create a `.env` file in the root directory and add your configuration settings:
