import requests, sqlite3, os, urllib, urllib2
from bs4 import BeautifulSoup as bs


# docset config
docset_name = 'algorithms-visualized.docset'
output = docset_name + '/Contents/Resources/Documents/'

# create docset directory
if not os.path.exists(output): os.makedirs(output)

# add icon
icon = 'https://dl.dropboxusercontent.com/u/12327637/algo-visualize.png'
urllib.urlretrieve(icon, docset_name + "/icon.png")


def update_db(name, path):

  typ = 'Guide'
  cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
  fetched = cur.fetchone()
  if fetched is None:
      cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
      print('DB add >> name: %s, path: %s' % (name, path))
  else:
      print("record exists")


def create_subdir(path, output):
  currentdir = output
  subdir = path.split('/')
  
  # if there's subfolder, create it and append it to current directory
  if len(subdir) > 1:
    for i in range(0, len(subdir) - 1, 2):
      currentdir = output + subdir[i] + '/'
  if not os.path.exists(currentdir): os.makedirs(currentdir)
  return currentdir


def download_page(currentdir, page_url, page):
  
  if len(page.split('/')) > 1:
    page = page.split('/')[-1]
  try:
    res = urllib2.urlopen(page_url)
    open(os.path.join(currentdir, page), 'wb').write(res.read())
    print "downloaded doc: ", page
  except:
    print " X"
    pass


def add_docs():

  root_url = 'http://www.cs.usfca.edu/~galles/visualization/Algorithms.html'

  # start souping index_page
  data = requests.get(root_url).text
  soup = bs(data)
  
  # add the title of index_page to db index
  page_title = 'Algorithms and Data structures visualized'
  index_page = root_url.split('/')[-1]
  update_db(page_title, index_page)

  
  # extract href(s) and name(s) from the index_page
  for link in soup.findAll('a'):
      name = link.text.strip()
      path = link.get('href')
      
      # add to db index with links needed
      filtered = ['source.html', 'bugfeature.html', 'about.html', 'Algorithms.html' ,'faq.html' ,'java/visualization.html' ,'flash.html', 'contact.html']
      if name is not None and not path.startswith('http') and path not in filtered:
        name = 'visualize ' + name
        update_db(name, path)


def add_infoplist():
  name = docset_name.split('.')[0]
  info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
         "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> " \
         "<plist version=\"1.0\"> " \
         "<dict> " \
         "    <key>CFBundleIdentifier</key> " \
         "    <string>{0}</string> " \
         "    <key>CFBundleName</key> " \
         "    <string>{1}</string>" \
         "    <key>DocSetPlatformFamily</key>" \
         "    <string>{2}</string>" \
         "    <key>isDashDocset</key>" \
         "    <true/>" \
         "    <key>isJavaScriptEnabled</key>" \
         "    <true/>" \
         "    <key>dashIndexFilePath</key>" \
         "    <string>{3}</string>" \
         "</dict>" \
         "</plist>".format(name, name, name, index_page)
  open(docset_name + '/Contents/info.plist', 'wb').write(info)


if __name__ == '__main__':
  db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
  cur = db.cursor()
  try:
      cur.execute('DROP TABLE searchIndex;')
  except:
      pass
      cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
      cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
  # start
  add_docs()
  add_infoplist()

  # # commit and close db
  db.commit()
  db.close()
