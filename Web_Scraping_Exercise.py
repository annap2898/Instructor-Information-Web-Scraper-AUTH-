import requests
from bs4 import BeautifulSoup
import lxml
import json

#function to extract email addresses from the parsed HTML content
def fetch_mail(soup):
    a_tags = soup.find_all("a")  #find all <a> tags
    mails_list = []

    for mail in a_tags:
        mail.getText()  #extract text from <a> tags
        if "@" in mail.getText():  #find the emails, using "@" to identify a pattern
            mails_list.append(mail.getText())
    return mails_list 

#function to process instructor information and categorize into titles, names, and last names
def fetch_info(info_list):
    title_list = []
    name_list = []
    last_list = []
    my_list = []

    for info in info_list:
        last_list.append(info[-1])  #append the last item in the info list (assumed last name)
        if len(info) == 3:
            title_list.append(info[0])  #αdd title to title list
            name_list.append(info[1])  #add name to name list
        elif len(info) == 5:
            title_list.append(info[0] + info[1])  #combine title (if they are two)
            name_list.append(info[2] + " " + info[3])  #combine first and middle name
        else:
            if len(info[-2]) <= 3:  #check if second last item is a middle name (only initials)
                title_list.append(info[0])
                name_list.append(info[1] + " " + info[2])  #combine first and middle name
            else:
                title_list.append(info[0] + info[1])  #combine title parts
                name_list.append(info[2])  #add name to name list
    my_list.append(title_list)
    my_list.append(name_list)
    my_list.append(last_list)

    return my_list

#function to create a dictionary of instructor information
def info_dict(titles, first_names, last_names, emails):
    combined_list = ["Title", "First Name", "Last Name", "e-mail"]
    mini_dict_list = []

    #create individual dictionaries for each instructor
    for index in range(len(titles)):
        combined_info = [titles[index], first_names[index], last_names[index], emails[index]]
        mini_dict = {}

        for i in range(4):  #map each piece of info to the corresponding key
            mini_dict[combined_list[i]] = combined_info[i]
        mini_dict_list.append(mini_dict)

    #create a larger dictionary indexed by last names
    mega_dict = {}
    for a in range(len(last_names)):
        mega_dict[last_names[a]] = mini_dict_list[a]
    return mega_dict


#fetching the webpage content
response = requests.get(url="https://websites.auth.gr/appbio/instructors/")
#parse the HTML content of the webpage
my_soup = BeautifulSoup(response.text, "lxml")

#find all instructor information sections
instructors_info = my_soup.find_all(class_="instructor_title")
#create an empty list to store each instructor's information as sublists
instructors_info_lists = []

#extract and process each instructor's information into structured lists
for info in instructors_info:
    instructors_info_lists.append(info.getText().split())

#remove the last element (|) from each sublist
for sublist in instructors_info_lists:
    if sublist:
        sublist.pop()

#extract emails using the fetch_mail function
my_mails = fetch_mail(my_soup)

#process instructor information using the fetch_info function
my_information = fetch_info(instructors_info_lists)

#separate processed information into titles, names, and last names
my_titles = my_information[0]
my_names = my_information[1]
my_last = my_information[2]

#create a dictionary with all instructor information
my_dict = info_dict(my_titles, my_names, my_last, my_mails)


#write the dictionary to a file using the json module
with open("Instructors_Info.txt", "w") as file:
    #use json.dump to write the dictionary as nested dictionaries
    json.dump(my_dict, file, indent=4)  # indent=4 to make it more clear and readable

print("Dictionary has been written to 'Instructors_Info.txt' in nested dictionary format.")
