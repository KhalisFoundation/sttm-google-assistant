import requests

def hukam():

  url = "http://old.sgpc.net/hukumnama/jpeg%20hukamnama/hukamnama.mp3"
  r = requests.get(url, allow_redirects=True)

  open('hukam.mp3','wb').write(r.content)
  print('Hukam saved successfully!')