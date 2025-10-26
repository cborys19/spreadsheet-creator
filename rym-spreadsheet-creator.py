# add information about release
#   artist
#   title
#   release year
#   composer (if necessary; might need to create separate logic for adapting classical lists)
#   genre family
#   sub-genres
#   month listened
#   day listened
#   runtime
#   format
#   personal rating

import re
import os
import csv

import verifier

fieldnames = ['artist', 'title', 'year', 'genre_family', 
              'subgenres', 'month', 'day', 'date', 
              'runtime', 'format', 'rating', 'link']
list_link_regex = re.compile(r"^https://rateyourmusic\.com/list/.+$")
release_link_regex = re.compile(r"^https://rateyourmusic\.com/release/.+$")
date_regex = re.compile(
    r"^(?:(?:0[13578]|1[02])/(?:0[1-9]|[12][0-9]|3[01])|"     # 31-day months
    r"(?:0[469]|11)/(?:0[1-9]|[12][0-9]|30)|"                 # 30-day months
    r"02/(?:0[1-9]|1[0-9]|2[0-8]))/\d{4}$|"                   # Feb 1–28
    r"^(?:02/29/(?:(?:(?:[02468][048]00)|"                    # Feb 29 leap years
    r"(?:[13579][26]00)|"
    r"(?:\d{2}(?:0[48]|[2468][048]|[13579][26])))))$"
)

def newSheetPrompt():
    sheet_name = input("Enter name of spreadsheet (preferably name of list): ")

    while True:        
        rym_list_link = input("Enter URL to list on Rate Your Music: ") # add URL validation via regex
        rym_list_link = verifier.verifyLink(list_link_regex, rym_list_link)
        if rym_list_link != -1:
            break
    
    while True:
        classical_flag = input("Is this a classical list? (yes or no): ").casefold() # need to parse for yes/no
        if classical_flag in ("yes", "no"):
            break
        else:
            print("ERROR: Please enter \"yes\" or \"no\"")

    sheet_data = [ sheet_name, rym_list_link, classical_flag ]

    return sheet_data

def editSheetPrompt():
    count = 0
    file_dict = {}
    files = os.listdir(".")
    csv_files = [f for f in files if f.endswith(".csv")]

    while True:
        print("Please select the CSV file you wish to edit")
        print("-------------------------------------------")
        for file in csv_files:
            count += 1
            print(f"\t{count} - {file}")
            file_dict.update({count: file})
        file_choice = input("File: ")

        file_choice = verifier.verifySheetChoice(file_choice, file_dict)
        if file_choice != -1:
            break
        else:
            count = 0
            file_dict.clear()
    print(f"Opening {file_choice} for editing...")
    return file_choice


def releasePrompt():
    artist = input("Enter name of release artist: ")
    title = input("Enter title of release: ")
    
    while True:
        release_year = input("Enter year of release: ")
        release_year = verifier.verifyYear(release_year)
        if release_year != -1:
            break

    genre_family = input("Enter genre family/families: ") # need logic to parse multiples

    subgenres = input("Enter subgenres of release: ")

    month_listened = ""
    day = ""
    date_listened = ""

    while True:
        runtime = verifier.verifyRuntime()
        if runtime != -1:
            break

    format = input("Enter release format: ")

    personal_rating = ""
    
    while True:
        rym_link = input("Enter URL to release on Rate Your Music: ") # add URL validation via regex
        rym_link = verifier.verifyLink(release_link_regex, rym_link)
        if rym_link != -1:
            break
    
    info_dict = {
        'artist': artist,
        'title': title,
        'year': release_year,
        'genre_family': genre_family,
        'subgenres': subgenres,
        'month': month_listened,
        'day': day,
        'date': date_listened,
        'runtime': runtime,
        'format': format,
        'rating': personal_rating,
        'link': rym_link
    }

    return info_dict

def mainMenu():
    print("What would you like to do?")
    print("\t1 - Make spreadsheet")
    print("\t2 - Edit an existing spreadsheet")
    print("\t9 - Exit")

    while True:
        choice = input("Selection: ")
        try:
            choice = int(choice)
            match choice:
                case 1:
                    new_sheet_options = newSheetPrompt()
                    sheetWriter(new_sheet_options)
                    break
                case 2:
                    edit_sheet_name = editSheetPrompt()
                    sheetEditor(edit_sheet_name)
                    break
                case 9:
                    exit()
                    break
                case _:
                    print("ERROR: Please enter a valid menu choice")
        except:
            print("ERROR: Please enter a valid number")

def entryEditor(releaseInfo):
    verifier.printReleaseInfo(releaseInfo)

    while True:
        while True:
            option = input("What field should be corrected?" \
                            "\n\t\t1 - Artist\n\t\t2 - Album" \
                            "\n\t\t3 - Release Year\n\t\t4 - Genre Family" \
                            "\n\t\t5 - Subgenres\n\t\t6 - Runtime" \
                            "\n\t\t7 - Format\n\t\t8 - Link" \
                            "\n\t\t0 - Return\n\tField: "
            )
            option = verifier.verifyOption(option)
            if option != -1:
                break

        match option:
            case 1: # Artist
                print(f"Artist originally entered: {releaseInfo['artist']}")
                new_artist = input("Enter edited artist: ")
                releaseInfo['artist'] = new_artist
                break
            case 2: # Title
                print(f"Title originally entered: {releaseInfo['title']}")
                new_title = input("Enter edited title: ")
                releaseInfo['title'] = new_title
                break
            case 3: # Release Year
                print(f"Year originally entered: {releaseInfo['year']}")
                while True:
                    new_year = input("Enter edited year of release: ")
                    new_year = verifier.verifyYear(new_year)
                    if new_year != -1:
                        releaseInfo['year'] = new_year
                        break
                break
            case 4: # Genre Family
                print(f"Genre family originally entered: {releaseInfo['genre_family']}")
                new_genre_family = input("Enter edited genre family: ")
                releaseInfo['genre_family'] = new_genre_family
                break
            case 5: # Subgenres
                print(f"Subgenres originally entered: {releaseInfo['subgenres']}")
                new_subgenres = input("Enter edited subgenres: ")
                releaseInfo['subgenres'] = new_subgenres
                break
            case 6: # Runtime
                while True:
                    print(f"Runtime originally entered: {releaseInfo['runtime']}")
                    new_runtime = verifier.verifyRuntime()
                    if new_runtime != -1:
                        releaseInfo['runtime'] = new_runtime
                        break
                break
            case 7: # Format
                print(f"Format originally entered: {releaseInfo['format']}")
                new_format = input("Enter edited format: ")
                releaseInfo['format'] = new_format
                break
            case 8: # Release link
                while True:
                    rym_link = input("Enter URL to release on Rate Your Music: ") # add URL validation via regex
                    rym_link = verifier.verifyLink(release_link_regex, rym_link)
                    if rym_link != -1:
                        releaseInfo['link'] = rym_link
                        break
                break

        verifier.printReleaseInfo(releaseInfo)
        
        while True:
            correct_check = input("Does the following information look correct? (\"Yes\" or \"No\"): ").casefold()
            if correct_check in ("yes", "no"):
                break
            else:
                print("ERROR: Please enter \"Yes\" or \"No\"")
    
        if correct_check == "yes":
            break
    
    return releaseInfo

def sheetWriter(sheetOptions):
    with open(f'{sheetOptions[0]}.csv', 'w', newline='') as spreadsheet:
        print("\nEntering new release...")
        print("------------------------")
 
        writer = csv.DictWriter(spreadsheet, dialect='excel', fieldnames=fieldnames)
        writer.writeheader()

        while True:
            release_info = releasePrompt()
            while True:
                verifier.printReleaseInfo(release_info)
                            
                correct_check = input("Does the following information look correct? (\"Yes\" or \"No\"): ").casefold()
                if correct_check in ("yes", "no"):
                    if correct_check == "yes":
                        writer.writerow(release_info)
                        print(f"\n\n{release_info['artist']} — {release_info['title']} has been written!\n\n")
                        break
                    else:
                        release_info = entryEditor(release_info)
                else:
                    print("ERROR: Please enter \"Yes\" or \"No\"")  

def sheetEditor(sheetName):
    with open(f'{sheetName}', 'a', newline='') as spreadsheet:
        print("\nEntering new release...")
        print("------------------------")

        writer = csv.DictWriter(spreadsheet, dialect='excel', fieldnames=fieldnames)

        while True:
            release_info = releasePrompt()
            while True:
                verifier.printReleaseInfo(release_info)
                            
                correct_check = input("Does the following information look correct? (\"Yes\" or \"No\"): ").casefold()
                if correct_check in ("yes", "no"):
                    if correct_check == "yes":
                        writer.writerow(release_info)
                        print(f"\n\n{release_info['artist']} — {release_info['title']} has been written!\n\n")
                        break
                    else:
                        release_info = entryEditor(release_info)
                else:
                    print("ERROR: Please enter \"Yes\" or \"No\"")                

def main():
    mainMenu()

if __name__ == "__main__":
    main()
