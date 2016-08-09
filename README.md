# lectureDL
## Setup:
lectureDL is written in [Python 3](http://python.org/downloads) and uses the [Selenium library](http://selenium-python.readthedocs.io) coupled with [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/).

The easiest way to install selenium is with pip:
	`pip3 install selenium`

To run lectureDL, download the zip file for this repository and execute the script with Python 3 from inside the directory:
	`python3 lectureDL.py`

Note: I'd recommend hiding subjects that are not active this semester because the script may try to find lecture recordings for past semesters.
![Subject list](https://github.com/larryhudson/lectureDL/subj_list_screenshot.png "Click on the gear to hide subjects")

## What it does:
* Logs in to Unimelb LMS system
* Builds list of subjects
* For each subject, navigate through to echo system
* Builds list of lectures
* For each lecture, builds filename based on subject number and date and downloads

## Features:
* Assigns week numbers based on date - formatted eg. "LING30001 Week 1 Lecture 2.m4a"
* Support for subjects with single or multiple lectures per week
* Skips if file already exists
* Can download either video files or audio files
* Allows user to choose specific subjects and to only download lectures for specific weeks

## To do list:
* Allow user to choose download folder
* Replace list system (eg. to_download) with class and attributes?
* Change Week numbering from Week 1 to Week 01 so they stay in order after Week 10
* Scroll down JavaScript list of lecture recordings - otherwise might have 'element not visible' error when trying to click