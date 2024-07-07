# Student Grouping Project

This project retrieves student data from Airtable, performs clustering analysis, and creates balanced groups which are then saved into an Excel file.

## Table of Contents

1. [Installation](#installation)
2. [Usage](#usage)
3. [Dependencies](#dependencies)
4. [License](#license)

## Installation

1. **Python Installation:**
   - Python 3 is required to run this project. If Python is not installed on your machine, you can download and install it from the [official Python website](https://www.python.org/downloads/).

2. **Installing Required Libraries:**
   - To install the necessary libraries to run the project, run the following command in your terminal or command prompt:
     ```
     pip install pandas pyairtable scikit-learn
     ```

3. **Setting up Airtable API Key and Base ID:**
   - Define your Airtable API key (`API`) and base ID (`base_id`) in the `keys.py` file:
     ```python
     API = "your_airtable_api_key_here"
     base_id = "your_airtable_base_id_here"
     table_name = "students"
     ```

## Usage

- To start the project, run the following command in your terminal or command prompt from the project directory:
