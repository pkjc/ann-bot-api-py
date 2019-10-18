import requests

resp = requests.get('https://clinical-trial-finder-api.herokuapp.com/api/v1/studies/search?description=aneurysm')
if resp.status_code != 200:
    # This means something went wrong.
    print('error')
for todo_item in resp.json():
    print('{}'.format(todo_item['brief_title']))