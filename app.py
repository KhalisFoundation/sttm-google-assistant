from flask import Flask, request, send_file
import better_translit as bt
import banidb
import hukam
import random
from datetime import date
app = Flask(__name__)

hukam.hukam()
lango = {'english':['en','bdb'],'punjabi':['pu','bdb'],'spanish':['es','sn'],'hindi':['hi','sts']} 
tdate = date.today()
y = tdate.year
m = tdate.month
d = tdate.day
cache = banidb.LRUCache('cache.dat',1)

@app.route('/') # this is the home page route
def hello_world(): # this is the home page function that generates the page code
    return "Hello world!"
    
@app.route('/webhook', methods=['POST'])
def webhook():
  req = request.get_json(silent=True, force=True)
  query_result = req.get('queryResult')
  print(query_result)
  action = query_result.get('action')
  json = {}
  if action == "get_hukamnama" :
    data = banidb.hukamnama()['hukam'][0]
    print(data)
    shabad_id = data['shabad_id']
    verses = data['verses']
    cache.put(tdate,(shabad_id,verses,'hukam'))
    fdata = [ver['verse'] for ver in verses]
    result = '\n'.join(fdata)
    json = {
      "payload": {
        "google": {
          "expectUserResponse": True,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "Here's the Hukamnama!",
                  "displayText": result
                }
              },
              {
                "mediaResponse": {
                  "mediaType": "AUDIO",
                  "mediaObjects": [
                    {
                      "contentUrl": "https://sttm-google-assistant.herokuapp.com/hukam",
                      "description": f"Hukamnama for {d}/{m}/{y}",
                      "icon": {
                        "url": "https://khalisfoundation.org/wp-content/uploads/2016/11/sttmicon-1-1024x660.png",
                        "accessibilityText": f"Hukamnama for {d}/{m}/{y}"
                      },
                      "name": "Hukamnama"
                    }
                  ]
                }
              },
              {
                "simpleResponse": {
                  "textToSpeech": "Wanna hear translations in?",
                  "displayText": "Translate to?"
                }
              }
            ],
            "suggestions": [
              {
                "title": "Punjabi"
              },
              {
                "title": "English"
              },
              {
                "title": "Spanish"
              },
              {
                "title": "Hindi"
              },
              {
                "title": "Skip"
              }
            ],
            "linkOutSuggestion": {
              "destinationName": "in Browser",
              "url": "https://www.sikhitothemax.org/hukamnama"
            }
          }
        }
      }
    }
    # print(result)
  

  elif action == 'hukamnama.hukamnama-translation':
    lang = query_result.get('parameters').get('language').lower()
    data = banidb.hukamnama(y,m,d)
    verses = data['hukam'][0]['verses']
    if cache.check(tdate)[0] is True:
      verses = cache.get()[tdate][1]
      langu = lango[lang]
      pu = True
      if langu[0] != 'pu':
        fdata = [ver['steek'][langu[0]][langu[1]] for ver in verses]
        pu = False
      else:
        fdata = [ver['steek'][langu[0]][langu[1]]['unicode'] for ver in verses if ver['steek'][langu[0]][langu[1]]['unicode'] is not None]
      result = '\n'.join(fdata)
    else:
      result = "Hukamnama changed recently!"      
    json = {
        "payload": {
          "google": {
            "expectUserResponse": True,
            "richResponse": {
              "items": [
                {
                  "simpleResponse": {
                    "textToSpeech": " ",
                    "displayText": result
                  }
                }
              ],
              "suggestions": [
                {
                  "title": "Go Back"
                },
                {
                  "title": "Explore Shabads"
                },
                {
                  "title": "Read Banis"
                },
                {
                  "title": "Sehaj Paath"
                },                
                {
                  "title": "Read Hukamnama"
                }
              ]
            }
          }
        }
      }
    json['payload']['google']['richResponse']['items'][0]['simpleResponse']['textToSpeech'] = result if not pu else f"<speak><voice name='pa-IN-Wavenet-A'><prosody rate='slow'>{bt.better(result)}</prosody></voice></speak>"


  elif action == "get_random":
    data = banidb.random()
    shabadID = data['shabad_id']
    print(f"shabad with id:{shabadID}")
    verses = data['verses']
    cache.put(tdate,(shabadID,verses,'random'))
    fdata = [ver['verse'] for ver in verses]
    result = '\n'.join(fdata)
    json = {
        "payload": {
          "google": {
            "expectUserResponse": True,
            "richResponse": {
              "items": [
                {
                  "simpleResponse": {
                    "textToSpeech": f"<speak><voice name='pa-IN-Wavenet-A'><prosody rate='slow'>{bt.better(result)}</prosody></voice></speak>",
                    "displayText":result
                  }
                },
                {
                  "simpleResponse": {
                    "textToSpeech": "Wanna hear translations in?",
                    "displayText": "Translate to?"
                  }
                }
              ],
              "suggestions": [
                {
                  "title": "Punjabi"
                },
                {
                  "title": "English"
                },
                {
                  "title": "Spanish"
                },
                {
                  "title": "Hindi"
                },
                {
                  "title": "Skip"
                }
              ],
              "linkOutSuggestion": {
                "destinationName": "Open in Browser",
                "url": f"https://www.sikhitothemax.org/shabad?id={shabadID}"
              }
            }
          }
        }
      }
  
  elif action == 'random.random-translation':
    lang = query_result.get('parameters').get('language').lower()
    if cache.check(tdate)[0] is True:
      verses = cache.get()[tdate][1]
    langu = lango[lang]
    pu = True
    if langu[0] != 'pu':
      fdata = [ver['steek'][langu[0]][langu[1]] for ver in verses]
      pu = False
    else:
      fdata = [ver['steek'][langu[0]][langu[1]]['unicode'] for ver in verses if ver['steek'][langu[0]][langu[1]]['unicode'] is not None]
    result = '\n'.join(fdata)
    json = {
        "payload": {
          "google": {
            "expectUserResponse": True,
            "richResponse": {
              "items": [
                {
                  "simpleResponse": {
                    "textToSpeech": " ",
                    "displayText": result
                  }
                }
              ],
              "suggestions": [
                {
                  "title": "Go Back"
                },
                {
                  "title": "One more Shabad"
                },
                {
                  "title": "Today's Hukamnama"
                },
                {
                  "title": "Sehaj Paath"
                },
                {
                  "title": "Read Banis"
                }
              ]
            }
          }
        }
      }
    json['payload']['google']['richResponse']['items'][0]['simpleResponse']['textToSpeech'] = result if not pu else f"<speak><voice name='pa-IN-Wavenet-A'><prosody rate='slow'>{bt.better(result)}</prosody></voice></speak>"
  
  elif action == "get_shabad" or action == "go_back":
    if action == "get_shabad":
      shabad_id = int(query_result.get('parameters').get('shabadID'))
      ok = ['','','shabad']
    else:
      ok = cache.get()[tdate]
      shabad_id = ok[0]
    data = banidb.shabad(shabad_id)
    verses = data['verses']
    print(f"shabad has id:{shabad_id}")
    cache.put(tdate,(shabad_id,verses,ok[2]))
    fdata = [ver['verse'] for ver in verses]
    result = '\n'.join(fdata)
    json = {
        "payload": {
          "google": {
            "expectUserResponse": True,
            "richResponse": {
              "items": [
                {
                  "simpleResponse": {
                    "textToSpeech": f"<speak><voice name='pa-IN-Wavenet-A'><prosody rate='slow'>{bt.better(result)}</prosody></voice></speak>",
                    "displayText":result
                  }
                },
                {
                  "simpleResponse": {
                    "textToSpeech": "Wanna hear translations in?",
                    "displayText": "Translate to?"
                  }
                }
              ],
              "suggestions": [
                {
                  "title": "Punjabi"
                },
                {
                  "title": "English"
                },
                {
                  "title": "Spanish"
                },
                {
                  "title": "Hindi"
                },
                {
                  "title": "Skip"
                }
              ],
              "linkOutSuggestion": {
                "destinationName": "in Browser",
                "url": f"https://sttm.co/shabad?id={shabad_id}"
              }
            }
          }
        }
      }
    if ok[2] == 'hukam':
      json = {
      "payload": {
        "google": {
          "expectUserResponse": True,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "Here's the Hukamnama!",
                  "displayText": result
                }
              },
              {
                "mediaResponse": {
                  "mediaType": "AUDIO",
                  "mediaObjects": [
                    {
                      "contentUrl": "https://sttm-google-actino.gurmeharsingh.repl.co/hukam",
                      "description": f"Hukamnama for {d}/{m}/{y}",
                      "icon": {
                        "url": "https://khalisfoundation.org/wp-content/uploads/2016/11/sttmicon-1-1024x660.png",
                        "accessibilityText": f"Hukamnama for {d}/{m}/{y}"
                      },
                      "name": "Hukamnama"
                    }
                  ]
                }
              },
              {
                "simpleResponse": {
                  "textToSpeech": "Wanna hear translations in?",
                  "displayText": "Translate to?"
                }
              }
            ],
            "suggestions": [
              {
                "title": "Punjabi"
              },
              {
                "title": "English"
              },
              {
                "title": "Spanish"
              },
              {
                "title": "Hindi"
              },
              {
                "title": "Skip"
              }
            ],
            "linkOutSuggestion": {
              "destinationName": "in Browser",
              "url": "https://www.sikhitothemax.org/hukamnama"
            }
          }
        }
      }
    }

  elif action == "shabad.shabad-translation" or action == "back.back-translation":
    lang = query_result.get('parameters').get('language').lower()
    if cache.check(tdate)[0] is True:
      verses = cache.get()[tdate][1]
    langu = lango[lang]
    pu = True
    if langu[0] != 'pu':
      fdata = [ver['steek'][langu[0]][langu[1]] for ver in verses]
      pu = False
    else:
      fdata = [ver['steek'][langu[0]][langu[1]]['unicode'] for ver in verses if ver['steek'][langu[0]][langu[1]]['unicode'] is not None]
    result = '\n'.join(fdata)
    json = {
        "payload": {
          "google": {
            "expectUserResponse": True,
            "richResponse": {
              "items": [
                {
                  "simpleResponse": {
                    "textToSpeech": " ",
                    "displayText": result
                  }
                }
              ],
              "suggestions": [
                {
                  "title": "Go Back"
                },
                {
                  "title": "One more Shabad"
                },
                {
                  "title": "Today's Hukamnama"
                },
                {
                  "title": "Sehaj Paath"
                },
                {
                  "title": "Read Banis"
                }
              ]
            }
          }
        }
      }
    json['payload']['google']['richResponse']['items'][0]['simpleResponse']['textToSpeech'] = result if not pu else f"<speak><voice name='pa-IN-Wavenet-A'><prosody rate='slow'>{bt.better(result)}</prosody></voice></speak>"

  elif action == "get_banis":
    fdata = banidb.banis()
    baniDict = {
      1:'gur-mantr',
      2:'japujee-saahib',
      4:'jaap-saahib',
      6:"tavai-prasaadh-sava'ye-(sraavag-su'dh)",
      9:'benatee-chauapiee-saahib',
      10:'anandh-saahib',
      21:'raharaas-saahib',
      23:'sohilaa-saahib'
    }
    blist = {baniDict[i]:fdata[i] for i in baniDict.keys()}
    sgUrl = "https://sttm.co/sundar-gutka/"
    json = {
      "payload": {
        "google": {
          "expectUserResponse": True,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "Select one of the options below to get started."
                }
              },
              {
                "carouselBrowse": {
                  "items": []
                }
              }
            ],
            "suggestions": [
                {
                  "title": "Download Now!"
                },
                {
                  "title": "Random Shabad"
                },
                {
                  "title": "Today's Hukamnama"
                },
                {
                  "title": "Sehaj Paath"
                }
              ]
          }
        }
      }
    }
    for bani in blist.keys():
      res = {
        "title": f"{blist[bani]['gurmukhiUni']}",
        "description": f"{bt.better_eng(blist[bani]['transliterations'].get('english')).title()}",
        "openUrlAction": {
          "url": f"{sgUrl}{bani}"
        }
      }
      json['payload']['google']['richResponse']['items'][1]['carouselBrowse']['items'].append(res)
    view = {
        "title": "View More Banis",
        "description": "Opens in Browser",
        "openUrlAction": {
          "url": "https://www.sikhitothemax.org/sundar-gutka"
        }
      } 
    json['payload']['google']['richResponse']['items'][1]['carouselBrowse']['items'].append(view)

  elif action == 'show_rehats':
    data = banidb.rehats()[0:2]
    rehatUrl = 'https://sttm.co/rehat-maryadha'
    rehatImgUrl = "https://khalisfoundation.org/wp-content/uploads/2016/11/Maryada.jpg"
    json = {
    "payload": {
      "google": {
        "expectUserResponse": True,
        "richResponse": {
          "items": [
            {
              "simpleResponse": {
                "textToSpeech": "Here is Sikh Rehat Maryada in both Gurmukhi and English alphabet. Click to read it."
              }
            },
            {
              "carouselBrowse": {
                "items": [
                  {
                    "title": f"{data[1]['rehat_name']}",
                    "openUrlAction": {
                      "url": f"{rehatUrl}/pb"
                    },
                    "description": "Alphabet: Gurmukhi",
                    "footer": "Click to read",
                    "image": {
                        "url": f"{rehatImgUrl}",
                        "accessibilityText": "Sikh Rehat Maryada"
                      }
                  },
                  {
                    "title": f"{data[0]['rehat_name']}",
                    "openUrlAction": {
                      "url": f"{rehatUrl}"
                    },
                    "description": "Alphabet: English",
                    "footer": "Click to read",
                    "image": {
                        "url": f"{rehatImgUrl}",
                        "accessibilityText": "Sikh Rehat Maryada"
                      }
                  }
                ]
              }
            }
          ],
              "suggestions": [
                {
                  "title": "Get Random Shabad"
                },
                {
                  "title": "Today's Hukamnama"
                },
                {
                  "title": "Sehaj Paath"
                },
                {
                  "title": "Read Banis"
                }
              ]
        }
      }
    }
  }

  elif action in ('get_ang','newpaath','ang_random'):
    if action == 'newpaath':
      ang_no = 1
    elif action == 'ang_random':
      ang_no = random.randint(1,1430)
    else:
      ang_no = int(query_result.get('parameters').get('AngNumber'))
    extra = ''
    not_okay = ang_no<1 or ang_no>1430
    if not_okay:
      extra = {
        "simpleResponse": {
          "textToSpeech": "There are 1430 angs of Gurbani treasure in Guru Granth Sahib ji. Better start from the very beginning.",
          "displayText": "Waheguru ji, There are 1430 angs in Guru Granth Sahib ji🙏"
        }
      }
      ang_no = 1
    json = {
      "payload": {
        "google": {
          "expectUserResponse": True,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "Click Read Ang to begin.",
                  "displayText": " "
                }
              },
              {
                "basicCard": {
                  "title": "Guru Granth Sahib ji",
                  "subtitle": f"Ang no. {ang_no}",
                  "formattedText": "To mantain the sanctity of Gurbani,\n ***Cover your head before proceeding!***",
                  "buttons": [
                    {
                      "title": "Read Ang",
                      "openUrlAction": {
                        "url": f"https://sttm.co/ang?ang={ang_no}"
                      }
                    }
                  ]
                }
              }
            ],
              "suggestions": [
                {
                  "title": "Sehaj Paath"
                },
                {
                  "title": "Get Random Shabad"
                },
                {
                  "title": "Today's Hukamnama"
                },
                {
                  "title": "Read Banis"
                }
              ]
          }
        }
      }
    }
    if not_okay and extra!='':
      json['payload']['google']['richResponse']['items'].insert(0,extra)

  elif action == 'get_amrit_keertan':
    fdata = banidb.amritkeertan()[0:10]
    akUrl = "https://sttm.co/index/amrit-keertan"
    akImgUrl = "https://khalisfoundation.org/wp-content/uploads/2018/10/amrit-kirtan-f.png"
    json = {
      "payload": {
        "google": {
          "expectUserResponse": True,
          "richResponse": {
            "items": [
              {
                "simpleResponse": {
                  "textToSpeech": "Waheguru ji, Click the button to read.",
                  "displayText": "Waheguru ji, Enjoy Gurbani!"
                }
              },
              {
                "basicCard": {
                  "title": "Amrit Keertan",
                  "formattedText": "Cover your head before proceeding!",
                  "image": {
                      "url": f"{akImgUrl}",
                      "accessibilityText": "Amrit Keertan"
                    },
                  "buttons": [
                    {
                      "title": "Read Now",
                      "openUrlAction": {
                        "url": f"{akUrl}"
                      }
                    }
                  ]
                }
              }
            ],
              "suggestions": [
                {
                  "title": "Get Random Shabad"
                },
                {
                  "title": "Today's Hukamnama"
                },
                {
                  "title": "Sehaj Paath"
                },
                {
                  "title": "Read Banis"
                }
              ]
          }
        }
      }
    }
  return json

@app.route('/hukam',methods=['GET'])
def hukam():
  return send_file("hukam.mp3",as_attachment=True)  

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
