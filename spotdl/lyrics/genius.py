import bs4, requests#, time
base_url = "https://genius.com"
base_search_url = base_url + "/api/search/multi?per_page=1&q="

class Genius():
    @classmethod
    def from_query(self,artist, song):
        query = "{} {} ".format(artist,song)
        # print("Artist name: {} \n Song:{}".format(artist, song))
        encoded_query = query.replace(" ", "+")
        search_url = base_search_url + encoded_query
        response_json = requests.get(search_url).json()
        lyric_url = base_url + response_json['response']['sections'][0]['hits'][0]['result']['path']
        return self.from_url(lyric_url)
    @classmethod
    def from_url(self,url):
        # time.sleep(0.5)
        soup = bs4.BeautifulSoup(requests.get(url).content, features='lxml')
        retries = 10
        lyrics = soup.html.p.text
        while retries > 0 and lyrics == "Produced by" or lyrics =="Featuring":
            # time.sleep(0.5)
            soup = bs4.BeautifulSoup(requests.get(url).content, features="lxml")
            lyrics = soup.html.p.text
        if retries == 0 and lyrics == "Produced by":
            # the scripts gives up and plays hangman
            # print("hangman")
            return ""
        return soup.html.p.text
