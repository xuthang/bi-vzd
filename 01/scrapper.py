from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests as req
import time
from time import sleep

myUrl='https://www.psp.cz/sqw/'
urlStart = myUrl + 'hlasovani.sqw?o=8'
encodingType = 'windows-1250'

voteCSV = "vote.csv"
tmpVoteCSV = "tmp.csv"
meetinCSV = "meeting.csv"
tmpMeetingCSV = "meetingtmp.csv"

fVote = open(voteCSV, "a", encoding=encodingType)
ftmp = open(tmpVoteCSV, "w", encoding=encodingType)
fMeeting = open(meetinCSV, "a", encoding=encodingType)
fMeetingtmp = open(tmpMeetingCSV, "w", encoding=encodingType)

import os
if(os.stat(voteCSV).st_size == 0) :
    fVote.write('name,' + 'political party,' + 'topicID,' + 'vote' + '\n')

if(os.stat(meetinCSV).st_size == 0) :
    fMeeting.write('topicID, ' + 'topicName, ' +  'meetingNum, ' + 'votingDate' + '\n')

def getSoup(url):
    for i in range(5):
        try:
            ret = soup(uReq(url).read(), "html.parser", from_encoding=encodingType) #czech iso encoding
            return ret
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")
        
    return None

containers = getSoup(urlStart).findAll("td", {"class": "col-number"})
topicId = 0

for i in range(len(containers)):
    container = containers[i]
    meetingContainers = getSoup(myUrl + container.a["href"]).find("div", {"id" : "main-content"})

    meetinghtml = getSoup(myUrl + meetingContainers.a["href"]) #all links send to same table meeting, just take the 1st one
    pageNum = 0
    while meetinghtml:
        print('schuze: ' + str(i) + ' | strana: ' + str(pageNum))
        meetingTableWhole =  meetinghtml.find("div", {"class" : "search-results"})
        meetingTable = meetingTableWhole.select("tr")[1:]

        for meetingTopic in meetingTable :
            votingTopic = meetingTopic.select("td")[3].text.replace(',', '-')
            meetingNum = meetingTopic.select("td")[0].text
            votingDate = meetingTopic.select("td")[4].text

            start_time = time.time()
            votingSoup = getSoup(myUrl + meetingTopic.a["href"])

            votingContent = votingSoup.find("div", {"id" : "main-content"})

            politParties = votingContent.find_all("h2", {"class" : "section-title center"})[1: - 1]

            politPartyNames = [party.text.split(" (")[0] for party in politParties]
            politPartiesVotes = votingContent.find_all("ul", {"class" : "results"})
            votes = zip(politPartyNames, politPartiesVotes)

            for v in votes:
                for personVote in v[1].find_all("li"):
                    ftmp.write( '"'  + personVote.a.text + '",' + v[0] + ',' + str(topicId) + ','  + personVote.span["class"][1] + '\n' )
            
            fMeetingtmp.write(str(topicId) + ',' + votingTopic + ',' + meetingNum + ',' + votingDate + '\n')

            topicId += 1
            sleep(max(0, 0.5 - (time.time() - start_time)))

        #checks if next pages exists, if yes then overwrites meetinghtml
        meetinghtml = ""
        pageBar = meetingTableWhole.find("span", {"class" : "pages"})
        if pageBar is not None :
            nextPage = pageBar.find("a", {"class" : "next"})
            if nextPage is not None :
                meetinghtml = getSoup(myUrl + nextPage["href"])
                pageNum +=1

    ftmp.close()
    ftmp = open(tmpVoteCSV, "r", encoding=encodingType)
    fVote.write(ftmp.read())
    ftmp.close()
    ftmp = open(tmpVoteCSV, "w", encoding=encodingType)

    fMeetingtmp.close()
    fMeetingtmp = open(tmpMeetingCSV, "r", encoding=encodingType)
    fMeeting.write(fMeetingtmp.read())
    fMeetingtmp.close()
    fMeetingtmp = open(tmpMeetingCSV, "w", encoding=encodingType)

    print('merging, done idx: ' + str(i))

