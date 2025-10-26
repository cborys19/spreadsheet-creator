import re

def printReleaseInfo(releaseInfo):
    print("\n\tArtist:", releaseInfo['artist'],
    " | Title:", releaseInfo['title'],
    " | Year:", releaseInfo['year'],
    " | Genre Family:", releaseInfo['genre_family'],
    " | Subgenres:", releaseInfo['subgenres'],
    " | Month Listened:", releaseInfo['month'],
    " | Day Listened:", releaseInfo['day'],
    " | Date Listened:", releaseInfo['date'],
    " | Runtime:", releaseInfo['runtime'],
    " | Format:", releaseInfo['format'],
    " | Rating:", releaseInfo['rating'],
    "\n\tLink:", releaseInfo['link'])

def verifyYear(yearInput):
    try:
        yearInput = int(yearInput)
        return yearInput
    except:
        print("ERROR: Please enter a valid date")
        return -1

def verifyRuntime():
    runtime_minutes = input("Enter runtime of the album in minutes: ")
    try:
        runtime_minutes = int(runtime_minutes)
    except:
        print("ERROR: Please enter a valid number of minutes")
        return -1
    
    runtime_seconds = input("Enter remaining seconds in runtime: ")
    try:
        runtime_seconds = int(runtime_seconds)
    except:
        print("ERROR: Please enter a valid number of seconds")
        return -1
    
    if runtime_minutes < 0 or runtime_seconds < 0:
        print("ERROR: Value must be at least 0")
        return -1
    elif runtime_seconds > 59:
        print("ERROR: Number of seconds cannot exceed 59, please increment the number of minutes instead")
        return -1

    return round((runtime_minutes + (runtime_seconds / 60)), 2)

def verifyLink(linkRegex, link):
    if linkRegex.match(link):
        return link
    else:
        print("ERROR: Please enter a valid Rate Your Music link")
        return -1

def verifyOption(option):
    try:
        option = int(option)
    except:
        print("ERROR: Please enter a valid option")
        return -1
    
    if 1 <= option <= 9:
        return option
    else:
        print("ERROR: Please enter a valid number that corresponds to a field to edit")
        return -1

def verifySheetChoice(choiceNum, fileDict):
    try:
        choiceNum = int(choiceNum)
    except:
        print("ERROR: Please enter a valid number that corresponds to a file to edit")
        return -1
    
    if choiceNum <= len(fileDict):
        return fileDict.get(choiceNum)
    else:
        print("ERROR: Number entered does not correspond to file, likely out of range")
        return -1
