import os,pickle
from flask import Flask , request,render_template,redirect,url_for
import requests,re,json
from lxml import html
from bs4 import BeautifulSoup
import sys
from urlextract import URLExtract
from googletrans import Translator
import imdb
res_session = requests.Session()
number1 = 1
number2 = 11
app = Flask(__name__)
@app.route('/')
def main():
  return render_template('loading.html')
@app.route('/edit',methods = ['POST', 'GET'])
def edit():
  if request.method == 'GET':
    return render_template('edit.html')
  elif request.method == 'POST':
    url_get = request.form["url_change"]
    data_save = {"url":url_get,"number_page":1}
    pickle.dump(data_save,open("data.txt","wb"))
    return f"<p>OK </p><br><p>URL: {url_get}</p>"
@app.route(f'/page',methods = ['POST', 'GET'])
def form():
  global number1,number2,page
  translator = Translator()
  link_next = None
  link_back = None
  data_load = pickle.load(open("data.txt","rb"))
  #url = 'https://www.imdb.com/search/title/?genres=comedy&explore=title_type,genres&title_type=tvSeries&ref_=adv_explore_rhs'
  url = data_load["url"]
  number_page = data_load["number_page"]
  number_page = int(number_page)
  r = res_session.get(url)
  if request.method == 'GET' or request.method == 'POST':
    button_trailer = request.form.get('trailer', None)
    button_run = request.form.get('run', None)
    button_next = request.form.get('next', None)
    button_back = request.form.get('back', None)
    if(request.method == 'GET'):
      for numberi in range(1,6):
        numberi = int(numberi)
        if number_page == numberi:
          add_number_get = numberi * 10
          number1 = add_number_get - 9
          number2 = add_number_get + 1
      button_run="run"
#-----------------------------------------------------------------------------
    if button_next:
      if number_page == 5:
        next = request.form["next"]
        next = 'https://www.imdb.com'+next
        url = next
        r = res_session.get(url)
        data_save = {"url":url,"number_page":1}
        pickle.dump(data_save,open("data.txt","wb"))
        number1 = 1
        number2 = 11
        button_run = "True"
      else:
        number_page_add = number_page + 1
        number_page_add = int(number_page_add)
        data_save = {"url":url,"number_page":number_page_add}
        pickle.dump(data_save,open("data.txt","wb"))
        number1 += 10
        number2 += 10
        check_back = True
        button_run = "True"
    if button_back:
      if number_page == 1:
        back = request.form["back"]
        back = 'https://www.imdb.com'+back
        url = back
        r = res_session.get(url)
        data_save = {"url":url,"number_page":5}
        pickle.dump(data_save,open("data.txt","wb"))
        number1 = 41
        number2 = 51
        button_run = "True"
      else:
        number_page_add = number_page - 1
        number_page_add = int(number_page_add)
        data_save = {"url":url,"number_page":number_page_add}
        pickle.dump(data_save,open("data.txt","wb"))
        number1 -= 10
        number2 -= 10
        button_run = "True"
#-----------------------------------------------------------------------------
    if button_trailer:
      tree = html.fromstring(r.content)
      value_t = request.form["trailer"]
      value_t = int(value_t)
      links = tree.xpath(f'//*[@id="main"]/div/div[3]/div/div[{value_t}]/div[3]/h3/a/@href')
      for link in links:
        link = link
        code = re.sub('[^0-9]','',link)
      r_link = res_session.get(f"https://www.imdb.com{link}")
      tree2 = html.fromstring(r_link.content)
      vis = tree2.xpath(f'//*[@id="__NEXT_DATA__"]/text()')
      for vi in vis:
        vi = vi.split('{"id":"vi')[1]
        vi = vi.split('","is')[0]
        vi = re.sub('[^0-9]','', vi)
      video_url = f"https://www.imdb.com/video/vi{vi}"
      r = res_session.get(url=video_url)
      soup = BeautifulSoup(r.text, 'html.parser')
      script =soup.find("script",{'type': 'application/json'})
      json_object = json.loads(script.string)
      videos = json_object["props"]["pageProps"]["videoPlaybackData"]["video"]["playbackURLs"]
      for i2 in range(0,8):
        vo = str(videos[i2])
        if "480" in vo:
          extractor = URLExtract()
          vo = extractor.find_urls(vo)[0]
          link_trailer = vo
          break
        else:
          pass
      try:
        ia = imdb.IMDb()
        series = ia.get_movie(code)
        ia.update(series, 'episodes')
        episodes = series.data['episodes']
        print(series)
        season = None
        esp = 0
        for i in episodes.keys():
            n = len(episodes[i])
            season = i
            esp += n
        number_episodes = [season,esp]
      except:
        number_episodes = ["?","?"]
      return render_template('trailer.html',link_trailer = link_trailer,number_episodes =number_episodes)
#-----------------------------------------------------------------------------
    if button_run:
      tree = html.fromstring(r.content)
      check_next = True
      try:
        sada = check_back
      except:
        check_back = False
      src_images = []
      run_time = []
      list_genre = []
      list_name = []
      list_rate = []
      list_story = []
      list_link = []
      list_number = []
      for i in range(number1,number2):
        #sys.stdout.write('\r'+ f"Loading... {i}")
        for story in tree.xpath(f"//*[@id='main']/div/div[3]/div/div[{i}]/div[3]/p[2]/text()"):
          if story:
            story = translator.translate(story, src = "en" ,dest='fa').text
            list_story.append(story)
          else:
            list_story.append("Nothing")
        for genre in tree.xpath(f"//*[@id='main']/div/div[3]/div/div[{i}]/div[3]/p[1]/span"):
          check_genre = str(genre.values())
          if check_genre == "['genre']":
            genre = genre.text
            genre = translator.translate(genre, src = "en" ,dest='fa').text
            list_genre.append(genre)
            checked_genre = True
            break
          else:
            checked_genre = False
        if checked_genre == False:
          list_genre.append("Nothing")
        for url_img in tree.xpath(f'//*[@id="main"]/div/div[3]/div/div[{i}]/div[2]/a/img/@loadlate'):
          def getURL(url):
            resize_factor = 9
            p = re.compile(".*UX([0-9]*)_CR0,([0-9]*),([0-9]*),([0-9]*).*") 
            match = p.search(url)
            if match:
                img_width = str(int(match.group(1)) * resize_factor)
                container_width = str(int(match.group(3)) * resize_factor)
                container_height = str(int (match.group(4)) * resize_factor)
                result = re.sub(r"(.*UX)([0-9]*)(.*)", r"\g<1>"+ img_width +"\g<3>", url)
                result = re.sub(r"(.*UX[0-9]*_CR0,[0-9]*,)([0-9]*)(.*)", r"\g<1>"+ img_width +"\g<3>", result)
                result = re.sub(r"(.*UX[0-9]*_CR0,[0-9]*,[0-9]*,)([0-9]*)(.*)", r"\g<1>"+ container_height +"\g<3>", result)
                return result
            else:
              p = re.compile(".*UY([0-9]*)_CR([0-9]*),([0-9]*),([0-9]*),([0-9]*).*") 
              match = p.search(url)
              if match:
                img_width = str(int(match.group(1)) * resize_factor)
                container_width = str(int(match.group(3)) * resize_factor)
                container_height = str(int (match.group(4)) * resize_factor)
                result = re.sub(r"(.*UY)([0-9]*)(.*)", r"\g<1>"+ img_width +"\g<3>", url)
                result = re.sub(r"(.*UY[0-9]*_CR([0-9]*),[0-9]*,)([0-9]*)(.*)", r"\g<1>"+ img_width +"\g<4>", result)
                result = re.sub(r"(.*UY[0-9]*_CR([0-9]*),[0-9]*,[0-9]*,)([0-9]*)(.*)", r"\g<1>"+ container_height +"\g<4>", result)
                result = result.replace("hhttp","http")
                return result
              else:
                result = "no3535no345914"
                return result
          src_img = getURL(url_img)
          if "no3535no345914" in str(src_img):
            src_images.append(url_img)
          else:
            src_images.append(src_img)
        names = tree.xpath(f'//*[@id="main"]/div/div[3]/div/div[{i}]/div[3]/h3/a/text()')
        for name in names:
          name = name
          try:
            list_name.append(f"{name}")
          except:
            list_name.append("Nothing")
        number_names = tree.xpath(f'//*[@id="main"]/div/div[3]/div/div[{i}]/div[3]/h3/span[1]/text()')
        for number_name in number_names:
          number_name = number_name
        try:
          list_number.append(f"{number_name} ")
        except:
          list_number.append("?. ")
        list_link.append(i)
        rates = tree.xpath(f'//*[@id="main"]/div/div[3]/div/div[{i}]/div[3]/div/div[1]/strong/text()')
        if rates:
          for rate in rates:
            rate = rate
            list_rate.append(rate)
        else:
          list_rate.append("Nothing")
        for item in tree.xpath(f"//*[@id='main']/div/div[3]/div/div[{i}]/div[3]/p[1]/span"):
          if "runtime" in item.classes:
            run_time.append(item.text)
            runtime = True
            break
          else:
            runtime = False
        if runtime == False:
          run_time.append("Nothing")
        elif runtime == True:
          pass
  r = res_session.get(url)
  tree = html.fromstring(r.content)
  for link_next in tree.xpath(f"//*[@class='lister-page-next next-page']/@href"):
    if link_next:
      link_next = link_next
      check_next = True
    else:
      link_next = None
      check_next = False
  if not link_next:
    link_next = "N"
    check_next = False
  for link_back in tree.xpath(f"//*[@class='lister-page-prev prev-page']/@href"):
    if link_back:
      link_back = link_back
      check_back = True
    else:
      link_back = None
      check_back = False
  number_item = re.sub('[^0-9]','', list_number[0])
  number_item = int(number_item)
  if number_item != 1:
    check_back = True
  listz = zip(list_name,list_genre,run_time,list_rate,list_story,list_link,src_images,list_number)
  return render_template('index.html',listz = listz,link_next = link_next,link_back = link_back,check_next=check_next ,check_back=check_back)
if __name__ == "__main__":
  app.run()
