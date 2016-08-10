#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from datetime import timedelta
import urllib
import os.path
from os.path import expanduser
import argparse
import configparser
from sys import argv
import getpass

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
		
def lms_login(parent, user, password):
	user_field = parent.find_element_by_css_selector("input[name=user_id]")
	user_field.send_keys(user)
	pass_field = parent.find_element_by_css_selector("input[name=password]")
	pass_field.send_keys(password)
	pass_field.send_keys(Keys.RETURN)

def get_subj_code(string):
	# string such as "LING30001_2016_SM2: Exploring Linguistic Diversity" is passed in 
	# split at ": " to separate subj_code and subj_name
	middle_split = string.split(": ")
	# subj_code == LING30001_2016_SM2, split at "_", string[0]
	subj_code = middle_split[0].split("_")[0]
	return subj_code
	

def get_subj_name(string):
	# string such as "LING30001_2016_SM2: Exploring Linguistic Diversity" is passed in 
	# split at ": " to separate subj_code and subj_name
	middle_split = string.split(": ")
	subj_name = ": ".join(middle_split[1:])
	return subj_name
	

# main function
def main():
	
	# setup config file. if it exists, load it
	config = configparser.ConfigParser()
	if os.path.isfile('lectureDL.ini'):
		config.read('lectureDL.ini')
	# if it doesn't exist, initialise default settings
	else:
		config['DEFAULT'] = {'download_path': 'home_dir', 'username': 'default', 'password': 'default'}
	
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
	skipped_lectures = []
	downloaded_lectures = []
	dates_list = []
	all_switch = False
	print("Welcome to lectureDL.py")
	
	# simple command-line args
	if len(argv) > 1:
		if "-v" in argv:
			download_mode = "video"
			print("-v argument passed. Videos will be downloaded.")
		elif "-a" in argv:
			download_mode = "audio"
			print("-a argument passed. Audio will be downloaded.")
		if "-all" in argv:
			all_switch = True
			print("-all argument passed. All lectures will be downloaded.")
		if "-clearconfig" in argv:
			if os.path.isfile('lectureDL.ini'):
				# delete 'user' section
				config.remove_section('user')
				print("Cleared configuration file")

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

	# set date range for lecture downloads
	if not all_switch:
		print("Would you like to download lectures from specific weeks or since a particular date?")
		while dates_list == []:
			valid_input = True
			print("Enter a range of weeks (eg. 1-5 or 1,3,4) or a date (DD/MM/2016) to download videos that have since been released.")
			user_dates_input = input("> ")

			# if left blank, download all videos
			if user_dates_input == "":
				dates_list = [start_week0 + datetime.timedelta(n) for n in range(int((datetime.datetime.today() - start_week0).days))]
	
			# if user enters comma-separated weeks, or just one, make a list for each and then concatenate
			elif "," in user_dates_input or user_dates_input.isdigit():
				chosen_weeks = user_dates_input.replace(" ", "").split(",")
	
				# validate to see if weeks are ints between 1 and 12 inclusive
				for item in chosen_weeks:
					if int(item) < 1 or int(item) > 12 or not item.isdigit():
						print("Invalid input. Weeks must be integers between 1 and 12 inclusive.")
						valid_input = False
	
				# build date lists for each week and then concatenate
				print("Lectures will be downloaded for: ")
				for item in chosen_weeks:
					start_date = start_week0 + (int(item) * week_delta)
					end_date = end_week0 + (int(item) * week_delta)
					dates_in_week = [start_date + datetime.timedelta(n) for n in range(int((end_date - start_date).days))]
					if valid_input:
						dates_list += dates_in_week
						print("Week ", item)

			# entering a week range or a start date both generate a range between start and end
			elif "-" in user_dates_input or "/" in user_dates_input:

				# validate to see if weeks are ints between 1 and 12 inclusive
				if "-" in user_dates_input:
					chosen_weeks = user_dates_input.split("-")
					for item in chosen_weeks:
						if int(item) < 1 or int(item) > 12 or not item.isdigit():
							print("Invalid input. Weeks must be integers between 1 and 12 inclusive.")
							valid_input = False
		
					# validate to check if end week comes after first week
					if chosen_weeks[1] > chosen_weeks[0]:
						start_week = chosen_weeks[0]
						end_week = chosen_weeks[1]
						start_date = start_week0 + (int(start_week) * week_delta)
						end_date = end_week0 + (int(end_week) * week_delta)
						if valid_input:
							dates_list = [start_date + datetime.timedelta(n) for n in range(int((end_date - start_date).days))]
					else:
						print("Invalid input. The second week must come after the first week.")
	
				elif "/" in user_dates_input:
					# if in DD/MM/YYYY format, create a range between start_date and today
					try:
						start_date = datetime.datetime.strptime(user_dates_input, "%d/%m/%Y")
						end_date = datetime.datetime.today() + day_delta
						dates_list = [start_date + datetime.timedelta(n) for n in range(int((end_date - start_date).days))]
					except ValueError:
						print("Invalid input. Enter string in the format DD/MM/YYYY.")
			
				# if list has been appended, print range		
				if not dates_list == []:
					print("Lectures will be downloaded for the dates between " + datetime.datetime.strftime(dates_list[0], "%d %B") + " and " + datetime.datetime.strftime(dates_list[-1], "%d %B"))

			# catch-all for anything else
			else:
				print("Invalid input")
		
	# if all_switch is true
	else:
		dates_list = [start_week0 + datetime.timedelta(n) for n in range(int((datetime.datetime.today() - start_week0).days))]

	# startup chrome instance
	print("Starting up Chrome instance")
	driver = webdriver.Chrome("ChromeDriver/chromedriver")
	print("Starting login process")
	driver.get("http://app.lms.unimelb.edu.au")
	
	# check config file for user settings, else ask for input
	if "user" in config:
		input_user = config["user"]["username"]
		input_password = config["user"]["password"]
	else:
		input_user = input("Please enter your username: ")
		input_password = getpass.getpass("Please enter your password: ")
	
	# run login function with user and pass	
	lms_login(driver, input_user, input_password)
	time.sleep(5)
	
	# offer to save user and pass in config file	
	if not "user" in config:
		print("Would you like to save your username and password for next time? (y/n)")
		save_choice = input("> ")
		if save_choice == "y":
			config["user"] = {"username": input_user,
			                  "password": input_password}
			print("Saving config file.")
			with open('lectureDL.ini', 'w') as configfile:
				config.write(configfile)
		else:
			print("Credentials not saved.")

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
		# call functions to get code and name
		subj_code = get_subj_code(full_string)
		subj_name = get_subj_name(full_string)
		# get subject link
		subj_link = link.get_attribute("href")
		# set default for checking against user-specified subjects
		skip_subj = False
		subject_list.append([subj_code, subj_name, subj_link, subj_num])
		# add one to subj_num counter
		subj_num += 1
	
	# create lists for subjects to download and skip
	user_subjects = []
	skipped_subjects = []
	
	if not all_switch:
		# print subjects to choose from
		print("Subject list:")
		for item in subject_list:
			# print subject code: subject title
			print(str(item[3]) +  ". " + item[0] + ": " + item[1])

		# choose from subjects to download
		while user_subjects == []:
			print("Please enter subjects you would like to download (eg. 1,2,3) or leave blank to download all ")
			user_choice = input("> ")
			if not user_choice == "":
				chosen_subj_nums = user_choice.split(",")
				for item in chosen_subj_nums:
					# validate to check if numbers are between 1 and however big the list is
					if int(item) < 1 or int(item) > len(subject_list) or not item.isdigit():
						print("Invalid input. Subject numbers must be between 1 and", str(len(subject_list)), "inclusive.")
					for subj in subject_list:
						if not int(item) == subj[3]:
							skipped_subjects.append(subj)
						else:
							user_subjects.append(subj)
			# if left blank, download all subjects
			else:
				user_subjects = subject_list
	
	# if all_switch is true
	else:
		user_subjects = subject_list
		
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
		recs_page = search_link_text(driver, ["Recordings", "Capture", "recordings", "capture"])
	
		# if no recordings page found, skip to next subject
		if recs_page is None:
			print("No recordings page found, can you find the name of the page?")
			# search for something else? ask user to input page
			search_input = input("> ")
			recs_page = search_link_text(driver, [search_input])
	
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
		# for each li element, build up filename info and add to download list
		for item in recs_list:
			# click on each recording to get different download links
			date_div = item.find_element_by_css_selector("div.echo-date")
			date_div.click()
			# scroll div so lectures are always in view
			driver.execute_script("return arguments[0].scrollIntoView();", date_div)
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

	print("Saving config file.")
	with open('lectureDL.ini', 'w') as configfile:
		config.write(configfile)
			
if __name__ == "__main__":
	main()