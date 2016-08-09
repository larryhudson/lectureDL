#!/usr/bin/env python3
# lectureDL.py by Larry Hudson
# Python script to download all lecture files, either video or audio
# What it does:
	# Logs in to Unimelb LMS system
	# Builds list of subjects
	# For each subject, navigate through to echo system
	# Builds list of lectures
	# For each lecture, builds filename based on subject number and date and downloads
# Features:
	# Assigns week numbers based on date - formatted eg. "LING30001 Week 1 Lecture 2.m4a"
	# Support for subjects with single or multiple lectures per week
	# Skips if file already exists
	# Can download either video files or audio files
	# Allows user to choose specific subjects and to only download lectures newer than a specific date
# To do list:
	# Allow user to choose download folder
	# Replace list system (eg. to_download) with class and attributes?
	# Change Week numbering from Week 1 to Week 01 (yeah yeah) - best boy Astrid xox

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from datetime import timedelta
import urllib
import os.path
from os.path import expanduser

# define function to find a link and return the one it finds
# works by making a list of the elements and sorts by descending list length,
# so it returns the one with length 1, avoiding the empty lists.
# if it can't find anything, it will return none
def search_link_text(parent, string_list):
	link_elements = []
	for string in string_list:
		link_elements.append(parent.find_elements_by_partial_link_text(string))
	sorted_list = sorted(link_elements, key=len, reverse=True)
	if sorted_list[0] == []:
		return None
	else:
		return sorted_list[0][0]

# setup download folders
home_dir = expanduser("~")
video_folder = os.path.join(home_dir, "Downloads/lectureDL/Lecture videos")
audio_folder = os.path.join(home_dir, "Downloads/lectureDL/Lecture audio")

# if they don't exist, make them
if not os.path.exists(video_folder):
	os.makedirs(video_folder)
if not os.path.exists(audio_folder):
	os.makedirs(audio_folder)

# build week number dictionary
current_date = datetime.datetime(2016, 7, 25)
start_week0 = datetime.datetime(2016, 7, 18)
end_week0 = datetime.datetime(2016, 7, 24)
day_delta = timedelta(days=1)
week_delta = timedelta(days=7)
week_counter = 1
day_counter = 1
week_day = {}

# assigns a week number to each date
while week_counter < 13:
	while day_counter < 8:
		week_day[current_date] = week_counter
		day_counter += 1
		current_date = current_date + day_delta
	week_counter += 1
	day_counter = 1
 				
# set defaults until user changes them
download_mode = "default"
user_dates_input = "default"
skipped_lectures = []
downloaded_lectures = []

print("Welcome to lectureDL.py")

# set download mode
while download_mode == "default":
	print("Enter 'v' to download videos or 'a' to download audio")
	user_choice = input("> ")
	if user_choice == "a":
		download_mode = "audio"
	elif user_choice == "v":
		download_mode = "video"
	elif user_choice == "x":
		exit()
	else:
		print("That wasn't an option.")

# old functionality
# specify specific subjects, or download all videos		
# while user_subjects == "default":
# 	print("Enter subject codes separated by ', ' or leave blank to download all")
# 	user_subjects_input = input("> ")
# 	if not user_subjects_input == "":
# 		user_subjects = user_subjects_input.split(', ')
# 	else:
# 		user_subjects = []

user_dates_input
# if user enters comma-separated weeks, make a list for each and then concatenate
print("Would you like to download lectures from specific weeks or since a particular date?")
while user_dates_input == "default":
	print("Enter a range of weeks (eg. 1-5 or 1,3,4) or a date (DD/MM/2016) to download videos that have since been released.")
	user_dates_input = input("> ")
	dates_list = []
	if user_dates_input == "":
		# if left blank, download all videos
		dates_list = [start_week0 + datetime.timedelta(n) for n in range(int((datetime.datetime.today() - start_week0).days))]
	elif "," in user_dates_input or user_dates_input.isdigit():
		# if user enters comma-separated weeks, or just one, make a list for each and then concatenate
		print("Lectures will be downloaded for: ")
		chosen_weeks = user_dates_input.replace(" ", "").split(",")
		for item in chosen_weeks:
			start_date = start_week0 + (int(item) * week_delta)
			end_date = end_week0 + (int(item) * week_delta)
			dates_in_week = [start_date + datetime.timedelta(n) for n in range(int((end_date - start_date).days))]
			dates_list += dates_in_week
			print("Week ", item)
	elif "-" in user_dates_input or "/" in user_dates_input:
		# create a table of dates between start date and end date 
		if "-" in user_dates_input:
			# splits the start and the end weeks
			chosen_weeks = user_dates_input.split("-")
			start_week = chosen_weeks[0]
			end_week = chosen_weeks[1]
			start_date = start_week0 + (int(start_week) * week_delta)
			end_date = end_week0 + (int(end_week) * week_delta)
		elif "/" in user_dates_input:
			# create a range between start_date and today
			start_date = datetime.datetime.strptime(user_dates_input, "%d/%m/%Y")
			end_date = datetime.datetime.today()
		dates_list = [start_date + datetime.timedelta(n) for n in range(int((end_date - start_date).days))]
		print("Lectures will be downloaded for the dates between " + datetime.datetime.strftime(start_date, "%d %B")
		 + " and " + datetime.datetime.strftime(end_date, "%d %B"))
	else:
		print("That wasn't an option")

# startup chrome instance
print("Starting up Chrome instance")
driver = webdriver.Chrome("chromedriver")

# login process
print("Starting login process")
driver.get("http://app.lms.unimelb.edu.au")
user_field = driver.find_element_by_css_selector("input[name=user_id]")
input_user = input("Enter your username: ")
user_field.send_keys(input_user)
pass_field = driver.find_element_by_css_selector("input[name=password]")
input_pass = input("Enter your password: ")
pass_field.send_keys(input_pass)
# clear screen to hide password
print("\n" * 100)
pass_field.send_keys(Keys.RETURN)
time.sleep(5)

# list items in list class "courseListing"
course_list = driver.find_element_by_css_selector("ul.courseListing")
# only get links with target="_top" to single out subject headings
course_links = course_list.find_elements_by_css_selector('a[target=_top]')
# list to be appended with [subj_code, subj_name, subj_link]
subject_list = [] 
subj_num = 1
# print status
print("Building list of subjects")

# get subject info from list of 'a' elements
for link in course_links:
	# get title eg "LING30001_2016_SM2: Exploring Linguistic Diversity"
	full_string = link.text
	# split at ": " to separate subj_code and subj_name
	middle_split = full_string.split(": ")
	# subj_code == LING30001_2016_SM2, split at "_", string[0]
	subj_code = middle_split[0].split("_")[0]
	# subj_name == Exploring Linguistic Diversity, string[1]
	# join/split method is to account for subjects such as "International Relations: Key Questions"
	subj_name = ": ".join(middle_split[1:])
	# get subject link
	subj_link = link.get_attribute("href")
	
	# set default for checking against user-specified subjects
	skip_subj = False
	subject_list.append([subj_code, subj_name, subj_link, subj_num])
	
	subj_num += 1

# print subjects to download
print("Subject list:")
for item in subject_list:
	# print subject code: subject title
	print(str(item[3]) +  ". " + item[0] + ": " + item[1])

# create lists for subjects to be added to
user_subjects = []
skipped_subjects = []

# choose subjects from list
print("Please enter subjects you would like to download (eg. 1,2,3) or leave blank to download all ")
user_choice = input("> ")

# for each chosen subj number, check if it is subj_num in subject list, if not skip it, if yes add it to subjects to be downloaded
if not user_choice == "":
	chosen_subj_nums = user_choice.split(",")
	for item in chosen_subj_nums:
		for subj in subject_list:
			if not item == str(subj[3]):
				skipped_subjects.append(subj)
			else:
				user_subjects.append(subj)
else:
	for subj in subject_list:
		user_subjects.append(subj)

print("Subjects to be downloaded:")
for item in user_subjects:
	# print subject code: subject title
	print(item[0] + ": " + item[1])
				
# for each subject, navigate through site and download lectures
for subj in user_subjects:
	# print status
	print("Now working on " + subj[0] + ": " + subj[1])
	
	# go to subject page and find Lecture Recordings page
	driver.get(subj[2])
	recs_page = search_link_text(driver, ["Recordings", "recordings", "Capture"])
	
	# if no recordings page found, skip to next subject
	if recs_page is None:
		print("No recordings page found, skipping to next subject")
		continue
	
	recs_page.click()
	
	# sometimes sidebar links goes directly to echo page, sometimes there's a page in between
	# if there's no iframe, it's on the page in between
	if len(driver.find_elements_by_tag_name("iframe")) == 0:
		links_list = driver.find_element_by_css_selector("ul.contentList")
		recs_page2 = search_link_text(links_list, ["Recordings", "Capture", "recordings", "capture"])
		
		recs_page2.click()
	time.sleep(4)
	
	# now on main page. navigate through iframes
	iframe = driver.find_elements_by_tag_name('iframe')[1]
	driver.switch_to_frame(iframe)
	iframe2 = driver.find_elements_by_tag_name('iframe')[0]
	driver.switch_to_frame(iframe2)
	iframe3 = driver.find_elements_by_tag_name('iframe')[0]
	driver.switch_to_frame(iframe3)
	
	# find ul element, list of recordings
	recs_ul = driver.find_element_by_css_selector("ul#echoes-list")
	recs_list = recs_ul.find_elements_by_css_selector("li.li-echoes")
	
	# setup for recordings
	subject_code = subj[0]
	multiple_lectures = False
	lectures_list = []
	to_download = [] # will be appended with [first_link, subject_code, week_num, lec_num, date]
	
	# print status
	print("Building list of lectures")
	scroll_wrapper = driver.find_elements
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	div.echoes-scroll-wrapper
	# for each li element, build up filename info and add to download list
	for item in recs_list:
		# click on each recording to get different download links
		date_div = item.find_element_by_css_selector("div.echo-date")
		date_div.click()
		time.sleep(2)
		
		# convert string into datetime.datetime object
		# date is formatted like "August 02 3:20 PM" but I want "August 02 2016"
		# so I need to get rid of time and add year
		date_string = " ".join(date_div.text.split(" ")[:-2]) + " 2016"
		date = datetime.datetime.strptime(date_string, "%B %d %Y")
		
		#lookup week number and set default lecture number
		week_num = week_day[date]
		lec_num = 1
		
		# get link to initial download page for either audio or video
		if download_mode == "audio":
			first_link = driver.find_element_by_partial_link_text("Audio File").get_attribute("href")
		else:
			first_link = driver.find_element_by_partial_link_text("Video File").get_attribute("href")
			
		# check if week_num is already in to_download
		for sublist in lectures_list:
			if sublist[2] == week_num:
				# set multiple_lectures to true so that filenames include lecture numbers
				multiple_lectures = True
				# add 1 to lec_num of earlier video
				sublist[3] += 1
				
		# add info to download list
		lectures_list.append([first_link, subject_code, week_num, lec_num, date])
		time.sleep(1)
	
	# assign filenames
	# made it a separate loop because in the loop above it's constantly updating earlier values etc
	for item in lectures_list:
		filename = item[1] + " Week " + str(item[2]) + " Lecture"
		if multiple_lectures == True:
			filename = filename + " " + str(item[3])
		if download_mode == "audio":
			filename_with_ext = filename + ".mp3"
			file_path = os.path.join(audio_folder, filename_with_ext)
		else:
			filename_with_ext = filename + ".m4v"
			file_path = os.path.join(video_folder, filename_with_ext)
		item.append(filename)
		item.append(file_path)
		
	# only add lectures to be downloaded if they are inside date range. else, skip them
	for item in lectures_list:
		if item[4] in dates_list and not os.path.isfile(item[6]):
			to_download.append(item)
		else:
			# if both outside date range and already exists
			if not item[4] in dates_list and os.path.isfile(item[6]):
				item.append("Outside date range and file already exists")
			# if just outside date range
			elif not item[4] in dates_list:
				item.append("Outside date range")
			# if just already exists
			elif os.path.isfile(item[6]):
				item.append("File already exists")
			skipped_lectures.append(item)
			print("Skipping " + item[5] + ": " + item[7])
	
	# print list of lectures to be downloaded
	if len(to_download) > 0:
		print("Lectures to be downloaded:")
		for item in to_download:
			print(item[5])
	else:
		print("No lectures to be downloaded.")
	
	# for each lecture, set filename and download
	for link in to_download:
		# link = [first_link, subject_code, week_num, lec_num, date, filename, file_path]
		# build up filename
		print("Now working on", link[5])
		# go to initial download page and find actual download link
		driver.get(link[0])
		time.sleep(1)
		dl_link = driver.find_element_by_partial_link_text("Download media file.").get_attribute("href")
		# send javascript to stop download redirect
		driver.execute_script('stopCounting=true') 
			
		# add file extension and build full download path
			
		 # check if file already exists
		if os.path.isfile(link[6]):
			print("File already exists. Skipping!")
			skipped_lectures.append(link)
			continue
		
		# download file using urllib.request.urlretrieve
		print("Downloading to ", link[6])
		urllib.request.urlretrieve(dl_link, link[6])
		print("Completed! Going to next file!")
		downloaded_lectures.append(link)
		time.sleep(2)
			
	# when finished with subject		
	print("Finished downloading files for", subj[1])
	
# when finished with all subjects	
print("All done!")

# [first_link, subject_code, week_num, lec_num, date]
# list downloaded lectures
if len(downloaded_lectures) > 0:
	if len(downloaded_lectures) == 1:
		print("Downloaded 1 lecture:")
	else:
		print("Downloaded " + str(len(downloaded_lectures)) + " lectures:")
	for item in downloaded_lectures:
		print(item[5])

# list skipped lectures
if len(skipped_lectures) > 0:
	if len(skipped_lectures) == 1:
		print("Skipped 1 lecture:")
	else:
		print("Skipped " + str(len(skipped_lectures)) + " lectures:")
	for item in skipped_lectures:
		print(item[5] + ": " + item[7])