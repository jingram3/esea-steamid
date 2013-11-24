# ESEA TF2 Steam ID parser/crawler
# takes a file name as a system argument to write out the IDs
# By Joe Ingram

from bs4 import BeautifulSoup
import requests
import re
import sys

DIVISIONS = ['http://play.esea.net/index.php?s=league&d=standings&division_id=2182', #invite
             'http://play.esea.net/index.php?s=league&d=standings&division_id=2183', #main
             'http://play.esea.net/index.php?s=league&d=standings&division_id=2184', #im
             'http://play.esea.net/index.php?s=league&d=standings&division_id=2185'] #open 

def getSteamID(player):
    image = player.find('img', alt='Team Fortress 2') #yikes
    if image is None: #no tf2-linked steamid
        return ''
    return image.parent.text.strip()

def getPlayerLinks(teamSoup):
    players = list()

    #terrible hack to get the rostered players and not recent visitors
    playerDiv = teamSoup.find('div', class_='sub-header bold margin-top')
    for p in playerDiv.find_all_next():
        paid = p.find('span', text='Paid') #only if they're paid
        if(paid):
            link=p.select('a[href^="/users/"]') #all user links
            if(len(link)>0 and link):
                players.append(link[0]['href'])
    return players

def main(outfile):
    cookie = dict()
    cookie['viewed_welcome_page'] = '1' #thanks to mthsad
    with open(outfile, 'w') as f:
        for div in DIVISIONS:
            r = requests.get(div, cookies=cookie)
            html = r.content
            divSoup = BeautifulSoup(html)
            for team in divSoup.select('a[href^="/teams/"]'): #all team links
                teamLink = 'http://play.esea.net' + team['href']
                teamSoup = BeautifulSoup(requests.get(teamLink, cookies=cookie).content)
                print(teamSoup.title)
                playerLinks = getPlayerLinks(teamSoup)
                for player in playerLinks:
                    playerLink = 'http://play.esea.net/' + player + '?tab=history'
                    playerSoup = BeautifulSoup(requests.get(playerLink, cookies=cookie).content)
                    print(playerSoup.title)
                    current = getSteamID(playerSoup)
                    if(len(current)>0): #found a tf2 steam ID
                        #ought to be in here somewhere...
                        m = re.match('^.*?([0-9]:[0-9]:[0-9]+?)$', current, re.DOTALL)
                        realID = m.groups()[0]
                        print(realID)
                        f.write(realID+"\n") #write to file

if __name__ == '__main__':
    main(sys.argv[1])
