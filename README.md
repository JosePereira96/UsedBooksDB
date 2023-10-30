# TradeStories Scrapper

## Overview

This web scraping program is designed to extract information from the used books selling marketplace TradeStories(https://tradestories.pt/) and store it in a local database. 

It utilizes Python's requests library, allowing users to build a robust and reliable HTTP connection to the website and define custom scraping rules to suit their specific needs.

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Configuration](#configuration)
5. [Best Practices](#best-practices)

## Features

This program is a tool I use that scrapes the website and extracts the new books added to the website, based on the genres and languages in which I'm interested. It stores the new entries in a local database and removes the books that have been sold. The code includes all the genre codes and language codes, making it possible to fully customize the query. 

- Customizable scraping rules
- Database upkeep (remove redundant entries, prevent duplicates, etc.)
- Parallel requests
- Logging and error handling for robustness





## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo.git
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the program with the following command:

   ```bash
   python scrape.py
   ```

2. Follow the prompts to input the target website and configure scraping rules.

3. The program will generate output files containing the scraped data.

## Configuration

The configuration file (`config.yml`) allows users to customize the program's behavior. Modify this file to adjust settings such as:

- User-agent string
- Throttling and rate-limiting parameters
- Output file format and location
- [Other relevant settings]

## Best Practices

- **Respect Robots.txt:** Always check and respect a website's `robots.txt` file to ensure compliance with its crawling policies.

- **Use Throttling:** Implement throttling to avoid sending too many requests in a short period, preventing server overload and potential IP blocking.

- **Dynamic Content:** If the website uses JavaScript to load content, consider using a headless browser or a library that can handle dynamic content.

- **Error Handling:** Implement robust error handling to manage unexpected situations and prevent crashes.