# CET1112 - Devbot.py Student Assessment Script
# Professor: Jeff Caldwell
# Year: 2023-09

# 1. Import libraries for API requests, JSON formatting, and epoch time conversion.
import requests
import json
import time

# 2. Complete the if statement to ask the user for the Webex access token.
choice = input("Do you wish to use the hard-coded Webex token? (y/n) ")

if choice.lower() == "n":
    accessToken = input("What is your access token? ")
    accessToken = "Bearer " + accessToken
else:
    accessToken = "Bearer ODMwOWQzNmEtZTU5Yi00OWQ1LTk0ZGMtMDRkY2IxMjJmYWE3NDZjN2E1YzQtOWQw_P0A1_a4f9c378-5de3-4ea4-ac12-58bb37777cfa"

# 3. Provide the URL to the Webex Teams room API.
r = requests.get("https://webexapis.com/v1/rooms", headers={"Authorization": accessToken})

# DO NOT EDIT ANY BLOCKS WITH r.status_code
if not r.status_code == 200:
    raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

# 4. Create a loop to print the type and title of each room.
print("List of rooms:")
rooms = r.json()["items"]
for room in rooms:
    print("Type: '{}' Name: {}".format(room["type"], room["title"]))

# SEARCH FOR WEBEX TEAMS ROOM TO MONITOR
# - Searches for user-supplied room name.
# - If found, print "found" message, else prints error.
# - Stores values for later use by bot.
# DO NOT EDIT CODE IN THIS BLOCK

while True:
    roomNameToSearch = input("Which room should be monitored for /location messages? ")
    roomIdToGetMessages = None

    for room in rooms:
        if room["title"].lower().find(roomNameToSearch.lower()) != -1:
            print("Found rooms with the word " + roomNameToSearch)
            print(room["title"])
            roomIdToGetMessages = room["id"]
            roomTitleToGetMessages = room["title"]
            print("Found room: " + roomTitleToGetMessages)
            break

    if roomIdToGetMessages is None:
        print("Sorry, I didn't find any room with '{}' in it.".format(roomNameToSearch))
        print("Please try again...")
    else:
        break

# WEBEX TEAMS BOT CODE
# Starts Webex bot to listen for and respond to /location messages.

while True:
    time.sleep(1)
    GetParameters = {"roomId": roomIdToGetMessages, "max": 1}
    # 5. Provide the URL to the Webex Teams messages API.
    r = requests.get("https://webexapis.com/v1/messages", params=GetParameters, headers={"Authorization": accessToken})

    if not r.status_code == 200:
        raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))

    try:
        json_data = r.json()
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:")
        print("Response content:", r.content)
        # Consider breaking out of the loop or handling this error based on your requirements
        continue

    if "items" not in json_data or len(json_data["items"]) == 0:
        print("No valid JSON data or no messages in the room.")
        # Consider breaking out of the loop or handling this condition based on your requirements
        continue

    messages = json_data["items"]
    message = messages[0]["text"]
    print("Received message: " + message)

    if message.startswith("/"):
        # 6. Provide your MapQuest API consumer key.
        mapsAPIGetParameters = {"location": location, "key": "wNE67B40qtT9HoSEzjv8i2BoybbCTDBp"}
        # 7. Provide the URL to the MapQuest GeoCode API.
        r = requests.get("https://www.mapquestapi.com/geocoding/v1/address", params=mapsAPIGetParameters)
        json_data = r.json()

        if not json_data["info"]["statuscode"] == 0:
            raise Exception("Incorrect reply from MapQuest API. Status code: {}".format(json_data["info"]["statuscode"]))

        locationResults = json_data["results"][0]["providedLocation"]["location"]
        print("Location: " + locationResults)

        # 8. Provide the MapQuest key values for latitude and longitude.
        locationLat = json_data["results"][0]["locations"][0]["displayLatLng"]["lat"]
        locationLng = json_data["results"][0]["locations"][0]["displayLatLng"]["lng"]
        print("Location GPS coordinates: {}, {}".format(locationLat, locationLng))

        ssAPIGetParameters = {"lat": locationLat, "lon": locationLng}
        # 9. Provide the URL to the Sunrise/Sunset API.
        r = requests.get("https://sunrisesunset.io/api/", params=ssAPIGetParameters)

        json_data = r.json()

        if not "results" in json_data:
            raise Exception("Incorrect reply from sunrise-sunset.org API. Status code: {}. Text: {}".format(r.status_code, r.text))

        # 10. Provide the Sunrise/Sunset key value for day_length.
        dayLengthSeconds = json_data["results"]["day_length"]
        sunriseTime = json_data["results"]["sunrise"]
        sunsetTime = json_data["results"]["sunset"]

        # 11. Complete the code to format the response message.
        responseMessage = "In {} the sun will rise at {} and will set at {}. The day will last {} seconds.".format(
            locationResults, sunriseTime, sunsetTime, dayLengthSeconds)
        print("Sending to Webex Teams: " + responseMessage)

        # 12. Complete the code to post the message to the Webex Teams room.
        HTTPHeaders = {"Authorization": accessToken, "Content-Type": "application/json"}
        PostData = {"roomId": roomIdToGetMessages, "text": responseMessage}

        r = requests.post("https://webexapis.com/v1/messages", data=json.dumps(PostData), headers=HTTPHeaders)

        if not r.status_code == 200:
            raise Exception("Incorrect reply from Webex Teams API. Status code: {}. Text: {}".format(r.status_code, r.text))
