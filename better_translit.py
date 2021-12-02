ikonkar = 'ੴ'
num = {
  '੧':'ਪਹਿਲਾ',
  '੨':'ਦੂਜਾ',
  '੩':'ਤੀਜਾ',
  '੪':'ਚੌਥਾ'}
numVa = ['੫','੬','੭','੮','੯','੧੦','੧੧','੧੨','੧੩','੧੪','੧੫','੧੬','੧੭']
ignore = ['।','॥']

def better(text):
  res = []
  words = text.split(' ')
  for ind, word in enumerate(words):
    if ikonkar in word:
      word = word.replace(ikonkar, 'ਇੱਕ ਓਅੰਕਾਰ')
    if len(word)>1:
      if word[0] in ignore:
        if '\n' in word:
          word = word.split('\n')[1]
          res.append("<break time='500ms'/>")
        else:
          continue
    if word not in ignore:
      if len(word)==1:
        if word in num.keys():
          word = num[word]
        elif word in numVa:
          word += "ਵਾਂ"
        else:
          word += "ਾ"
      else:
        if len(word)>2:
          if word[-1] == 'ਿ':
            if word[-2] not in ['ਹ','ੲ']:
              word = word[:-1]
          elif word[-1] == 'ੁ':
            if word[-2] not in ['ਹ','ੳ']:
              word = word[:-1]
      res.append(word)
  res = ' '.join(res)
  return res

def better_eng(text):
  text = text.replace('(n)','n')
  text = text.replace("'","")
  return text