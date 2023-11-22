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

### Customizable scraping rules
This program scrapes the website and extracts the new books, based on the user's prefered genres and languages which are defined in the `config.ini` file. This configuration file includes genre codes and language codes - parameters that can be used in the query - that the website currently supports, making it possible to fully customize the query by adding the relation in the **[genre_language_relation]** table. For example, if a user wants to search the website for fantasy books either in english or portuguese and science fiction books exclusively in english, the table **[genre_language_relation]** in the `config.ini` file should look like:

```
[genre_language_relation]
fantasy-english=1
fantasy-portuguese=1
non_fiction-english=1
```
The genre and language are separated by a `-`. This values are case sensitive. The value after the `=` sign is irrelevant. To remove a relation from the query, either comment (add a `;` character at the beggining of line) or delete the line. In the future, the code will take into account the value after the `=` sign and only interpret as boolean (0 = False, 1 = True) and ignore other values. 


### Database upkeep 
Everytime the program runs, it stores the new entries in the `recently_added` table of the local database. After finding a book that is present in the `books` table, it stops creating new requests, merges the tables and clears the `recently_added` table. 
Furthermore, since a book can have more than one genre associated, when a book is found in the `recently_added` table, its genre is updated to include the new genre. 
These features ensure that there are no duplicates in the database.

To remove redundant books, meaning, books that have been sold and are no longer present in the website but are still in the database, a process starts where it checks if each book's associated URL page is still active. This is a very time costly process, even when done in parallel, since there are thousands of entries.

### Parallel requests
Since web requests are the most time costly operation in this program, they are done asynchronously. Also, the batch size, meaning, the number of pages that are queried at once, can be configured in the `config.ini` file. 

### Logging and error handling
Currently, the program logs its results to a `.txt` file after sucefully completing. Error handling is a a feature to be added.


## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/JosePereira96/UsedBooksDB.git
   ```

2. Navigate to the project directory:

```bash
cd UsedBooksDB
```


3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. Open the `config.ini` file.

2. Update the following parameters:
   - `[database]` Table
      - `user`: Replace with the user that connects to the database created previously.
      - `password`: Replace with the user's password.
      - `dbName`: Specify the name of the database previously created.

   `[genre_language_relation]` Table
   - Add entries according to the rules mentioned above.

## Usage

1. Run the program with the following command:

   ```bash
   python3 scrapper.py
   ```

2. The program will print some status messages as it's running. Once finished, the database will be updated - possibly with new entries - and the `log.txt` file will also be updated with relevant information regarding the runtime.  

## Database Schema

The database will have two identicall tables named `books` and `recently_added` with the following columns:

- `BookID` (auto-incremented)
- `Title` (Book Title)
- `Author` (Book Author(s))
- `Price` (Asked price)
- `Genre` (Book Genre)
- `Language` (Book's Language)
- `CreatedBy` (Username of Book Owner)
- `PageURL` (URL to the Book's Post)
- `ImageURL` (URL to Book's Images)
- `DateAdded` (Date added to database)

Initially, the `recently_added` table will be empty. The new books will be added to this table and once the program finds a book that already belongs to the `books` table, it stop requesting new pages, merge the two tables and clear the `recently_added`


## Contributing

Feel free to contribute to the project by opening issues or submitting pull requests. Your feedback and suggestions are highly appreciated.


## Acknowledgments

- Thanks to the developers of the TradeStories website.
- Special thanks to the open-source community for their valuable contributions.

Happy coding!