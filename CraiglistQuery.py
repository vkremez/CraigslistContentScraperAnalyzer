# coding: utf-8
# iPython


# In[1]:

import pandas as pd
get_ipython().magic(u'pylab inline')


# In[2]:

import requests


# In[3]:

url_base = 'http://newyork.craigslist.org/search/brk/roo'
params = dict(max_price=600, private_room=1)
rsp = requests.get(url_base, params=params)


# In[4]:

print(rsp.url)


# In[5]:

print(rsp.text[:500])


# In[6]:

from bs4 import BeautifulSoup as bs4
html = bs4(rsp.text, 'html.parser')
print(html.prettify()[:1000])


# In[7]:

rooms = html.find_all('p', attrs={'class': 'row'})
print(len(rooms))


# In[8]:

this_room = rooms[15]
print(this_room.prettify())


# In[10]:

size = this_room.findAll(attrs={'class': 'pnr'})[0].text
print(size)


# In[16]:

this_time = this_room.find('time')['datetime']
this_time = pd.to_datetime(this_time)
this_price = float(this_room.find('span', {'class': 'price'}).text.strip('$'))
this_title = this_room.find('a', attrs={'class': 'hdrlnk'}).text
this_location = this_room.findAll(attrs={'class': 'pnr'})[0].text


# In[17]:

print('\n'.join([str(i) for i in [this_time, this_price, this_title, this_location]]))


# In[18]:

loc_prefixes = ['brk', 'mnh', 'que']


# In[19]:

def find_prices(results):
    prices = []
    for rw in results:
        price = rw.find('span', {'class': 'price'})
        if price is not None:
            price = float(price.text.strip('$'))
        else:
            price = np.nan
        prices.append(price)
    return prices

def find_times(results):
    times = []
    for rw in room:
        if time is not None:
            time = time['datetime']
            time = pd.to_datetime(time)
        else:
            time = np.nan
        times.append(time)
    return times


# In[22]:

results = []  # We'll store the data here
# Careful with this...too many queries == your IP gets banned temporarily
search_indices = np.arange(0, 300, 100)
for loc in loc_prefixes:
    print loc
    for i in search_indices:
        url = 'https://newyork.craigslist.org/search/{0}/roo'.format(loc)

        resp = requests.get(url, params={'room': 1, 's': i})
        txt = bs4(resp.text, 'html.parser')
        room = txt.findAll(attrs={'class': "row"})
        
     
        # Find the title and link
        title = [rw.find('a', attrs={'class': 'hdrlnk'}).text
                      for rw in apts]
        links = [rw.find('a', attrs={'class': 'hdrlnk'})['href']
                 for rw in apts]
        
        # Find the time
        time = [pd.to_datetime(rw.find('time')['datetime']) for rw in apts]
        price = find_prices(apts)
        
        # We'll create a dataframe to store all the data
        data = np.array([time, price, title, links])
        col_names = ['time', 'price', 'title', 'link']
        df = pd.DataFrame(data.T, columns=col_names)
        df = df.set_index('time')
        
        # Add the location variable to all entries
        df['loc'] = loc
        results.append(df)
        
# Finally, concatenate all the results
results = pd.concat(results, axis=0)


# In[26]:

results[['price']] = results[['price']].convert_objects(convert_numeric=True)


# In[27]:

results.head()


# In[28]:

ax = results.hist('price', bins=np.arange(0, 10000, 100))[0, 0]
ax.set_title('Brooklyn Room', fontsize=20)
ax.set_xlabel('Price', fontsize=18)
ax.set_ylabel('Count', fontsize=18)


# In[32]:

import string
use_chars = string.ascii_letters +    ''.join([str(i) for i in range(10)]) +    ' /\.'
results['title'] = results['title'].apply(
    lambda a: ''.join([i for i in a if i in use_chars]))

results.to_csv('craigslist_results.csv')


# In[43]:

import gmail
import time
import email


# In[38]:

gm = gmail.GMail('[gmail]', ‘[pass]')
gm.connect()
base_url = 'http://newyork.craigslist.org/'
url = base_url + 'search/brk/roo?max_price=600&private_room=1'
use_chars = string.ascii_letters + ''.join([str(i) for i in range(10)]) + ' '


# In[ ]:

link_list = []  # We'll store the data here
link_list_send = []  # This is a list of links to be sent
send_list = []  # This is what will actually be sent in the email
while True:
    resp = requests.get(url)
    txt = bs4(resp.text, 'html.parser')
    room = txt.findAll(attrs={'class': "row"})
    
    # We're just going to pull the title and link
    for roo in room:
        title = roo.find_all('a', attrs={'class': 'hdrlnk'})[0]
        name = ''.join([i for i in title.text if i in use_chars])
        link = title.attrs['href']
        if link not in link_list and link not in link_list_send:
            print('Found new listing')
            link_list_send.append(link)
            send_list.append(name + '  -  ' + base_url+link)
            
    # Flush the cache if we've found new entries
    if len(link_list_send) > 0:
        print('Sending mail!')
        msg = '\n'.join(send_list)
        m = email.message.Message()
        m.set_payload(msg)
        gm.send(m, ['[gmail]')
        link_list += link_list_send
        link_list_send = []
        send_list = []
    
    # Sleep a bit so CL doesn't ban us
    sleep_amt = np.random.randint(60, 120)
    time.sleep(sleep_amt)
