import requests
import json
import pandas as pd

headers = {"Authorization": "Bearer "} # Place the API Key here


def run_query(query, variables):
    request = requests.post("https://api.smash.gg/gql/alpha", json={"query": query, "variables": variables},
                            headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


tournaments_query = """
query TournamentsByTimeFrameAndCountry($cCode: String!, $perPage: Int!,
$beforeDate: Timestamp!, $afterDate: Timestamp!, 
  $videogameId: ID!) {
  tournaments(query: {
    perPage: $perPage
    sortBy: "startAt asc"
    filter: {
      countryCode: $cCode
      beforeDate: $beforeDate
      afterDate: $afterDate
      videogameIds: [$videogameId]
    }
  }){
    pageInfo{
      total
      totalPages
    }
  
    nodes {
      id
      name
      ownerId
      url(relative:false)
      
      countryCode
      region
      city
      postalCode
      venueName
      venueAddress
      
      lat
      lng
      mapsPlaceId
      
      primaryContactType
      contactTwitter
      contactEmail
      
      startAt
      endAt
      state
      
      hasOfflineEvents
      
      events {
        id
        name
        slug
        type
        videogameId
      }
      
      links {
        facebook
        discord
      }
    }
  }
  },
"""
tournaments_variables = {
    "cCode": "DE",
    "perPage": 100,
    "beforeDate": 1556582400,
    "afterDate": 1554076800,
    "videogameId": 1386
}


tournaments_json = run_query(tournaments_query, tournaments_variables)


# Deletes event entries from the dictionary and returns a full dictionary with the cleansed entries
def clean_videogameid(tournaments_dict):
    import re

    temp_dict = tournaments_dict

    for counter_node, node in enumerate(temp_dict["data"]["tournaments"]["nodes"]):
        # Check if Event is really an offline event
        if not node["hasOfflineEvents"]:
            print("Going to delete: %s @Clutch23" %str(temp_dict["data"]["tournaments"]["nodes"][counter_node]["name"]))
            del temp_dict["data"]["tournaments"]["nodes"][counter_node]
        for counter_event, event in enumerate(node["events"]):
            # Check if event is an Smash Ultimate event
            if event["videogameId"] != 1386: # 1386 = Game ID of Smash Ultimate
                print("going to delete: %s from %s" % (str(temp_dict["data"]["tournaments"]["nodes"][counter_node]["events"][counter_event]["name"]),str(temp_dict["data"]["tournaments"]["nodes"][counter_node]["name"])))
                del temp_dict["data"]["tournaments"]["nodes"][counter_node]["events"][counter_event]

            # check if an event is an doubles or an ladder event
            elif re.search("doubles | ladder",event["name"], flags= re.IGNORECASE):
                print("going to delete: %s from %s" % (str(temp_dict["data"]["tournaments"]["nodes"][counter_node]["events"][counter_event]["name"]), str(temp_dict["data"]["tournaments"]["nodes"][counter_node]["name"])))
                del temp_dict["data"]["tournaments"]["nodes"][counter_node]["events"][counter_event]


    return temp_dict

tournaments_df = pd.DataFrame(tournaments_json["data"]["tournaments"]["nodes"])

print(tournaments_variables)
print(tournaments_json)
print(type(tournaments_json))
print(tournaments_json["data"])
cleansed_json = clean_videogameid(tournaments_json)

