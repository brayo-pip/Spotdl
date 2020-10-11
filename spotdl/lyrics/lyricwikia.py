import bs4, requests
base_url = "https://genius.com"
base_search_url = base_url + "/api/search/multi?per_page=1&q="

class Genius():
    def from_query(artist, song):
        query = "{} {} ".format(artist,song)
        encoded_query = query.replace(" ", "+")
        search_url = base_search_url + encoded_query
        response_json = requests.get(search_url).json()
        lyric_url = base_url + response_json['response']['sections'][0]['hits'][0]['result']['path']
        return lyric_url
    
    def from_url(url):
        soup = bs4.BeautifulSoup(requests.get(url).content, features='lxml')
        return soup.html.p.text

#print(Genius.from_url(Genius.from_query("J Cole", "Middle Child")))