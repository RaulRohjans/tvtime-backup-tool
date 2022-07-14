# TV Time Backup Tool
This is a tool made in Python that allows users to backup saved shows (and their progress) from an account in TV Time.
Special thanks to [Kwbmm](https://github.com/Kwbmm) for creating [this](https://github.com/Kwbmm/scraped-tvtime-api) tool, from which I took snippets of code to build the scaper part of the tool.


## Installation 
To install the packages, simply navigate into the folder where the files are located and use pip the following way:

```
pip install -r requirements.txt
```


## Usage
To start the app, simply navigate into the project folder and run the following command:

```
python main.py
```

The first time the app is ran, a configuration file will be generated where you can define you MySQL instance details and TV Time account credentials. Make sure you provide and empty database the first time you set this up. All the tables will be created automatically!
After this is configured, when the program is re-executed, it should start saving data onto the database.
