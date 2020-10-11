from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests as req
import time
from time import sleep

myUrl='https://www.psp.cz/sqw/'
urlStart = myUrl + 'hlasovani.sqw?o=8'
encodingType = 'windows-1250'

meetinCSV = "newMeeting.csv"
tmpMeetingCSV = "meetingtmp.csv"

fMeeting = open(meetinCSV, "a", encoding=encodingType)
fMeetingtmp = open(tmpMeetingCSV, "w", encoding=encodingType)

import os
if(os.stat(meetinCSV).st_size == 0) :
    fMeeting.write('topicID,' + 'topicName,' +  'meetingNum,' + 'votingDate' + '\n')

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

            fMeetingtmp.write(str(topicId) + ',' + votingTopic + ',' + meetingNum + ',' + votingDate + '\n')
            topicId += 1

        #checks if next pages exists, if yes then overwrites meetinghtml
        meetinghtml = ""
        pageBar = meetingTableWhole.find("span", {"class" : "pages"})
        if pageBar is not None :
            nextPage = pageBar.find("a", {"class" : "next"})
            if nextPage is not None :
                meetinghtml = getSoup(myUrl + nextPage["href"])
                pageNum +=1

    fMeetingtmp.close()
    fMeetingtmp = open(tmpMeetingCSV, "r", encoding=encodingType)
    fMeeting.write(fMeetingtmp.read())
    fMeetingtmp.close()
    fMeetingtmp = open(tmpMeetingCSV, "w", encoding=encodingType)

    print('merging, done idx: ' + str(i))

