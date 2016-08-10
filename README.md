# lectureDL
## Setup:
lectureDL is written in [Python 3](http://python.org/downloads) and uses the [Selenium library](http://selenium-python.readthedocs.io) coupled with [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/). Note: lectureDL is setup to run on Mac, and will need a little bit of work before it reliably runs on Windows.

The easiest way to install selenium is with pip:
	`pip3 install selenium`

To run lectureDL, download the zip file for this repository and execute the script with Python 3 from inside the directory:
	`python3 lectureDL.py`

lectureDL can be run with the following command-line arguments:
* `-v` to download videos
* `-a` to download audio
* `-all` to download all lectures available
* `-path <download directory>` to change download directory inside home folder (eg. on a Mac `python3 lectureDL.py -path "Lecture recordings"` will save lectures inside `/Users/username/Lecture recordings`
*  `-clearconfig` to clear the config file (ie. forget user credentials and reset download folder)

These commands can be combined, for example `python3 lectureDL.py -v -all` will download all lecture videos available, which is the fastest way of running the script if you have your credentials saved in the configuration file. However, `-v -a` will not download both the video and the audio yet!

Note: I'd recommend hiding subjects that are not active this semester because the script may try to find lecture recordings for past semesters.

![Subject list](img/subj_list_screenshot.png?raw=true "Click on the gear to hide subjects")

## What it does:
* Logs in to Unimelb LMS system
* Builds list of subjects
* For each subject, navigate through to echo system
* Builds list of lectures
* For each lecture, builds filename based on subject number and date and downloads

## Features:
* Assigns week numbers based on date and appends lecture numbers if there are more than one lecture per week - formatted eg. "LING30001 Week 1 Lecture 2.m4v"
* Skips if file already exists
* Can download either video files or audio files
* Allows user to choose specific subjects and to only download lectures for specific weeks
* Can save username and password in configuration file, if the user wants
