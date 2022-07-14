import os.path
import json
import mysql.connector

# File Imports
from Utils import Login, Shows

# Global vars and Constants
db_connection = None
configuration = {
    "db": {
        "host": '',
        "port": '3306',
        "database": '',
        "user": '',
        "password": ''
    },
    "tv_time": {
        "user": '',
        "password": '',
        "session_key": 'my super secret key',
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 "
                          "Safari/537.36 "
        }
    }
}


# Methods
def start_cfg():
    global configuration
    cfg_path = os.path.join('config', 'config.json')

    if os.path.exists(cfg_path):
        # If file exists, read it
        with open(cfg_path) as f:
            configuration = json.load(f)
            f.close()

        verify_cfg()

        if not start_db():
            print('Could not start the database connection.".\n'
                  + 'Please make sure the settings are correct and try again!')
            exit()

    else:
        # Otherwise, create an empty file and exit
        if not os.path.exists('config'):
            os.makedirs('config')

        with open(cfg_path, 'w') as f:
            json.dump(configuration, f, indent=2)
            f.close()

        print('No configuration file detected, a blank one was crated at "config/config.json".\n'
              + 'Please make sure the settings are correct and try again!')
        exit()


def verify_cfg():
    global configuration

    if not configuration['db'] or not configuration['tv_time']:
        print('The provided configuration file has some mistakes".\n'
              + 'Please make sure the settings are correct and try again!')
        exit()

    if (
            not configuration['db']['user'] or not configuration['db']['password']
            or not configuration['db']['host'] or not configuration['db']['port']
            or not configuration['db']['database']
    ):
        print('There are errors in the database configuration".\n'
              + 'Please make sure the settings are correct and try again!')
        exit()

    if (
            not configuration['tv_time']['user'] or not configuration['tv_time']['password']
            or not configuration['tv_time']['session_key'] or not configuration['tv_time']['http_headers']
            or not configuration['tv_time']['http_headers']['User-Agent']
    ):
        print('There are errors in the TV Time credentials configuration".\n'
              + 'Please make sure the settings are correct and try again!')
        exit()


def checkTableExists(dbcon, table_name):
    global configuration

    db_cur = dbcon.cursor()
    db_cur.execute("""
        SELECT TABLE_SCHEMA
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(table_name.replace('\'', '\'\'')))
    res = db_cur.fetchall()
    if len(res) < 1:
        db_cur.close()
        return False

    for row in res:
        if str(row[0]).strip() == str(configuration['db']['database']).strip():
            db_cur.close()
            return True

    db_cur.close()
    return False


def start_db():
    global db_connection
    global configuration

    try:
        db_connection = mysql.connector.Connect(host=configuration['db']['host'],
                                                port=configuration['db']['port'],
                                                database=configuration['db']['database'],
                                                user=configuration['db']['user'],
                                                password=configuration['db']['password'])
        if not db_connection.is_connected():
            return False

        # Create database tables if needed
        if not checkTableExists(db_connection, 'series'):
            # Create series
            cursor = db_connection.cursor()
            cursor.execute("CREATE TABLE `series` (" +
                           "`id` int NOT NULL," +
                           "`name` mediumtext," +
                           "`progress` varchar(150)," +
                           "`time` varchar(150)," +
                           "PRIMARY KEY (`id`)," +
                           "UNIQUE KEY `id_UNIQUE` (`id`)" +
                           ")")
            cursor.close()

        if not checkTableExists(db_connection, 'season'):
            # Create season
            cursor = db_connection.cursor()
            cursor.execute("CREATE TABLE `season` (" +
                           "`id` int NOT NULL AUTO_INCREMENT," +
                           "`name` mediumtext," +
                           "`number_of_episodes` int," +
                           "`series` int," +
                           "PRIMARY KEY (`id`)," +
                           "UNIQUE KEY `id_UNIQUE` (`id`)," +
                           "KEY `fk_season_series_idx` (`series`)," +
                           "CONSTRAINT `fk_season_series` FOREIGN KEY (`series`) REFERENCES `series` (`id`)" +
                           ")")
            cursor.close()

        if not checkTableExists(db_connection, 'episode'):
            # Create episode
            cursor = db_connection.cursor()
            cursor.execute("CREATE TABLE `episode` (" +
                           "`id` int NOT NULL," +
                           "`number` int," +
                           "`name` mediumtext," +
                           "`air_date` date," +
                           "`watched` bit(1)," +
                           "`season` int," +
                           "PRIMARY KEY (`id`)," +
                           "UNIQUE KEY `id_UNIQUE` (`id`)," +
                           "KEY `fk_episode_season_idx` (`season`)," +
                           "CONSTRAINT `fk_episode_season` FOREIGN KEY (`season`) REFERENCES `season` (`id`)" +
                           ")")
            cursor.close()

        return True
    except Exception as e:
        print('The following error has ocurred while checking the database configuration:')
        print(e)
        exit()


def change_series(series):
    global db_connection

    try:
        cursor = db_connection.cursor()
        cursor.execute("select count(*) as qtd from series where id=%(id)s", {
            'id': series['id']
        })
        res = cursor.fetchone()
        if res[0] > 0:
            cursor.execute("update series set name=%(name)s, progress=%(progress)s, "
                           "time=%(time)s where id=%(id)s", {
                               'name': series['name'],
                               'progress': series['progress'],
                               'time': series['time'],
                               'id': series['id']
                           })
        else:
            cursor.execute("insert into series(id, name, progress, time) " +
                           "values(%(id)s, %(name)s, %(progress)s, %(time)s)", {
                               'id': series['id'],
                               'name': series['name'],
                               'progress': series['progress'],
                               'time': series['time']
                           })
        db_connection.commit()
        cursor.close()
    except Exception as e:
        print("The following error as occurred while trying to add a series:")
        print(e)
        exit()


def change_season(season, seriesID):
    global db_connection

    try:
        cursor = db_connection.cursor()
        cursor.execute("select count(*) as qtd from season where series=%(series)s and name=%(name)s", {
            'series': seriesID,
            'name': season['name']
        })
        res = cursor.fetchone()
        if res[0] > 0:
            cursor.execute(
                "update season set name=%(name)s, number_of_episodes=%(number_of_episodes)s, "
                "series=%(seriesID)s where series=%(seriesID)s and name=%(name)s", {
                    'name': season['name'],
                    'number_of_episodes': season['number_of_episodes'],
                    'seriesID': seriesID
                })
            db_connection.commit()

            cursor.execute("select id from season where series=%(series)s and name=%(name)s limit 1", {
                'series': seriesID,
                'name': season['name']
            })
            res = cursor.fetchone()
            cursor.close()
            return res[0]
        else:
            cursor.execute("insert into season(name, number_of_episodes, series) " +
                           "values(%(name)s, %(number_of_episodes)s, %(series)s)", {
                               'name': season['name'],
                               'number_of_episodes': season['number_of_episodes'],
                               'series': seriesID
                           })
            db_connection.commit()

            cursor.execute("SELECT LAST_INSERT_ID()")
            res = cursor.fetchone()
            cursor.close()
            return res[0]

    except Exception as e:
        print("The following error as occurred while trying to add a season:")
        print(e)
        exit()


def change_episode(episode, seasonID):
    global db_connection

    try:
        cursor = db_connection.cursor()
        cursor.execute("select count(*) as qtd from episode where id=%(id)s", {'id': episode['id']})
        res = cursor.fetchone()
        if res[0] > 0:
            cursor.execute("update episode set number=%(number)s, name=%(name)s, "
                           "air_date=%(air_date)s, watched=" + f"{'1' if episode['watched'] else '0'}, " +
                           "season=%(season)s where id=%(id)s", {
                               'number': episode['number'],
                               'name': episode['name'],
                               'air_date': episode['air_date'] if str(episode['air_date']).strip() != '' else 'NULL',
                               'season': seasonID,
                               'id': episode['id']
                           })
        else:
            cursor.execute("insert into episode(id, number, name, air_date, watched, season) " +
                           "values(%(id)s, %(number)s, %(name)s, %(air_date)s, "
                           f"{'1' if episode['watched'] else '0'}" + ", %(season)s)", {
                               'id': episode['id'],
                               'number': episode['number'],
                               'name': episode['name'],
                               'air_date': episode['air_date'] if str(episode['air_date']).strip() != '' else None,
                               'season': seasonID
                           })
        db_connection.commit()
        cursor.close()
    except Exception as e:
        print("The following error as occurred while trying to add a episode:")
        print(e)
        exit()


def main():
    global configuration
    global db_connection

    # Read and check the config
    print("Importing configuration...")
    start_cfg()
    if db_connection is None:
        print('Database credentials could not be read".\n'
              + 'Please make sure the settings are correct and try again!')
        exit()
    print("Done!\n")

    # Login into TV Time
    print("Logging into TV Time...")
    user_obj = Login.do_login(configuration['tv_time']['user'], configuration['tv_time']['password'],
                              configuration['tv_time']['http_headers'])
    if user_obj is None:
        print('Could not login to TV Time with the provided credentials".\n'
              + 'Please make sure the settings are correct and try again!')
        exit()
    print("Done!\n")

    # Fetch all added shows
    print("Fetching shows and updating database...")
    series = Shows.get_shows(configuration['tv_time']['http_headers'], user_obj)

    if len(series) < 1:
        print("Nothing to add, exiting...")
        exit()

    for s in series:
        # Save/Update series
        change_series(s)

        # Save/Update Seasons
        seasons = Shows.get_show(s['id'], configuration['tv_time']['http_headers'], user_obj)
        for season in seasons:
            seasonID = change_season(season, s['id'])

            for episode in season['episodes']:
                change_episode(episode, seasonID)

    print("Done!")


if __name__ == '__main__':
    # Start
    main()
