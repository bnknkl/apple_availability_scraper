import time
import requests
import json

# Apple variables

# Use this list to choose local stores to filter from.
# Apple search results choose the 12 closest stores to your zip code, which
# can mean very far away stores.

local_stores = [

]

# Put the models you want to search for here.
# Format: ["ModelID", "FriendlyModelName"]
# FriendlyModelName can be whatever you want. ModelID has to be the Apple model
# ID, WITHOUT the /A. This breaks the URL formatting and is added manually.

models = [

]

zip_code = "" # Put your search zip code in here.

# Slack variables

slack_webhook = ""

def check_inventory():

    availability = []

    for store in local_stores:
        availability.append({store: []})

    for model in models:
        print(f"Checking for {model[0]}/A ({model[1]})")
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 5_1_1 like Mac OS X; en) AppleWebKit/534.46.0 (KHTML, like Gecko) CriOS/19.0.1084.60 Mobile/9B206 Safari/7534.48.3',
        }
        url = f'http://www.apple.com/shop/retail/pickup-message?pl=true&parts.0={model[0]}%2FA&location={zip_code}'
        response = requests.get(url, headers=headers)
        response_json = response.json()
        stores = response_json['body']['stores']

        for store in stores:
            name = store['storeName']
            avail = store['partsAvailability'][model[0]+'/A']['pickupDisplay']
            if avail == 'available':
                if name not in local_stores:
                    continue

                print("FOUND ONE")
                print(f"- {name}")

                for stores in availability:
                    for store in stores:
                        if store == name:
                            stores[store].append(f"{model[0]}/A - {model[1]}")

        time.sleep(2)

    return availability

def send_slack_message(payload):

    headers = {
        "Content-type": "application/json"
    }

    message = {
    	"blocks": [
    		{
    			"type": "section",
    			"text": {
    				"type": "mrkdwn",
    				"text": "*Apple Device Availability*"
    			}
    		}
        ]
    }

    for stores in payload:
        for store in stores:
            joined_list = ", ".join(stores[store])
            message['blocks'].append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{store}*"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"{stores[store]}"
                    }
                ]
            }
         )

    r = requests.post(slack_webhook, headers=headers, json=message)

    print(r.text)

def main():
    if slack_webhook == "":
        check_inventory()
        print("No Slack webhook destination defined, so no Slack message going out.")
    else:
        send_slack_message(check_inventory())

if __name__ == "__main__":
    main()
