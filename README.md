# About

A small Python command-line client for interacting with an AudioBookShelf server

### WARNING

This program is under development and may error in interesting and unusal ways.  It's highly recommneded to ensure your Audiobookself database is backed up before using this tool. 

Additionally, while this tool should work on Windows and MacOS, it is currently untested on both,  Your milage may vary.

### Features

- List libraries, collections, series, genres and books with a simple filtering option.

- Powerful search feature for books

- Create or Update collections based on the result of a search.

### Overview

ABSCLI is a CLI wrapper around the AudioBookShelf HTTP API. It reads connection details from a per-user config file and exposes subcommands to list resources, query books (via DuckDB), create/update collections from queries, and run safe-guarded fixups.  

### Requirements

- Audiobookshelf 2.29.0 or newer
- Python 3.10 or newer  
- Dependencies:  
  - requests >= 2.32.5  
  - duckdb >= 0.9.0  
  - numpy >= 1.24.0  
  - pandas >= 2.0.0  

### Installation

1) Clone the repository
   
   ```bash
   git clone https://github.com/Undergrid/abscli.git
   cd absc
   ```

2) Create and activate the virtual environment
   
   ```bash
   python -m venv .venv
   
   On Linux/MacOS:
   source .venv/bin/activate
   
   On Windows Powershell:
   .venv\Scripts\Activate.ps1
   ```

3) Install dependencies
   
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

ABSCLI loads configuration files from the user config directory.  

- Path: ~/.config/abscli/<name>.json  
- The --server argument corresponds to <name> (with or without .json). Example: --server prod uses ~/.config/audiobookshelfcollector/prod.json  

Required JSON fields:  

- base_url: Base URL of your AudioBookShelf server (e.g., https://abs.example.com)  
- api_key: A valid API key for that server  

Example (~/.config/abscli/prod.json):  

`{  
  "base_url": "https://abs.example.com",  
  "api_key": "YOUR_API_KEY"  
}  `

Notes  

- If the file is missing or contains invalid JSON, the program exits with an error.  
- If base_url or api_key are missing, a descriptive error is raised.  

### Usage

#### General syntax

```
python abscli.py <command> [options]


Options:
    --server string             Specify the config for the server
    --library string            Specify the library to use
    --help                      Show help

Command:
    list                        Lists items of the specified type.
         libraries                  All libraries on the server.
         collections                All collections on the server or in
                                    a specific library
         series                     All series in a specific library
         genres                     All genres in a specific library
         books                      All books in a specific library
    
    info                        Displays useful information
         fields                     List of fields amd shortcuts that 
                                    can be used in the --where clause
                                    
    search                      Search for books in a specific library

    create collection           Search for books in a specific library
                                and create a collection containing them.
                                If a collection already exists, it will
                                not be modified.

    update collection           Search for books in a specific library
                                and create or update a collection 
                                containing them.
                                If a collection already exists, any books
                                not already in the collection will be
                                added.

List Options:

    --with-id                   'list' commands (except genres) will 
                                include the GUID of the item
    --seperator string          Output will be fields seperated by the
                                specified string without spaces

Filtering Options - used with the 'list' command:

    --filter string             Searches for the specified string as a
                                substring in the title of each item.
    --exact                     Filter string is matched exactly, not as
                                a substring
    --field                     When using 'list books', specify the field
                                to filter by (see 'info fields'). Defaults
                                to the book title,


Search Options - used with 'search', 'create' and 'update':

    --where string              Search query
    --sort string               Field to sort by
    --direction {asc, desc}     Sort order
    --display col [col ...]     A space seperated list of columns to 
                                display.
    --dryrun                    Perform the command without updating the
                                sever.

Additional 'create' and 'update' options:

    --name string               Name of the collection to create
                                or update
```

#### List Examples

List all libraries on the server.

```bash
python abscli.py list libraries --server abs --with-id
```

List all collections on the server.

```bash
python abscli.py list collections --server abs --with-id
```

List collections in a library called audiobooks.

```bash
python abscli.py list collections --server abs --library audiobooks --with-id
```

List book series in a library called audiobooks containing the word Chronicles

```bash
python abscli.py list series --server abs --library audiobooks --filter Chronicles --with-id
```

List book series in a library called audiobooks matching the phrase "Some Series"

```bash
python abscli.py list series --server abs --library audiobooks --filter "Some Series" --exact --with-id
```

#### Search Examples

The Search, Create, and Update commands all use the same search syntax, so you can replace "search" in the examples below with either "create collection" or "update collection".

List books in a library called audiobooks with a series containing the word Chronicles using a case insensitive match

```bash
python abscli.py search --server abs --library audiobooks --where "_SERIES ILIKE '%Chronicles%'" --name Chronicles 
```

Create a collection of books where the title starts with 'The" and the author name includes 'Joe'

```
python abscli.py search --server abs --library audiobooks --where "_TITLE LIKE 'The%' AND _AUTHOR LIKE "%Joe%"" --name "The Joe"
```

#### Where Syntax

The --where option accepts an expression that would be acceptable by duckdb's WHERE clause.  This include comparison operators (<, >, <=, >=, =, ==, <> or !=), logical operators (and, or, not, like, ilike etc) and many more.

Note that these are applied to a local copy of the list of books from the server, so you can't really break anything by getting this wrong.  The worst that could happen is a new empty collection or a program exception.

#### Shortcuts

Many fields have long names that contain period characters that are hard to remember of need to be quoted in a specific way.  A number of simple shortcuts are available to use instead of the more complex field name.  These shortcuts can be used in both the --where and --columns parameters.

You can retrieve a list of currently supported shortcuts in a particular library using the command:

```
python abscli.py info fields --server <server> --library <library>
```

Enries that show 'None' in the shortcut column do not currently have a shortcut.

##### Current shortcuts are:

| Field                            | Shortcut     |
| -------------------------------- | ------------ |
| media.id                         | _MEDIAID     |
| media.metadata.title             | _TITLE       |
| media.metadata.titleIgnorePrefix | _SHORTTITLE  |
| media.metadata.subtitle          | _SUBTITLE    |
| media.metadata.authorName        | _AUTHOR      |
| media.metadata.authorNameLF      | _AUTHORLF    |
| media.metadata.narratorName      | _NARRATOR    |
| media.metadata.seriesName        | _SERIES      |
| media.metadata.genres            | _GENRES      |
| media.metadata.publishedYear     | _PUBLISHYEAR |
| media.metadata.publishedDate     | _PUBLISHDATE |
| media.metadata.publisher         | _PUBLISHER   |
| media.metadata.description       | _DESCRIPTION |
| media.metadata.isbn              | _ISBN        |
| media.metadata.asin              | _ASIN        |
| media.metadata.language          | _LANGUAGE    |
| media.metadata.explicit          | _EXPLICIT    |
| media.metadata.abridged          | _ABRIDGED    |
| media.coverPath                  | _COVER       |
| media.tags                       | _TAGS        |
| media.numTracks                  | _TRACKS      |
| media.numAudioFiles              | _FILES       |
| media.numChapters                | _CHAPTERS    |
| media.duration                   | _DURATION    |
| media.size                       | _SIZE        |
