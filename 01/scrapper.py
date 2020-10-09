from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests as req
import pandas as pd
import numpy as np
from pprint import pprint
from time import sleep

myUrl='https://www.psp.cz/sqw/'
urlStart = myUrl + 'hlasovani.sqw?o=8'

voteFile = "vote.csv"
fVote = open(voteFile, "w")
meetingFile = "vote.csv"
fMeeting = open(meetingFile, "w")

def getSoup(url):
    return soup(uReq(url).read(), "html.parser", from_encoding="iso-8859-2") #czech iso encoding


containers = getSoup(urlStart).findAll("td", {"class": "col-number"})

#for container in containers:
container = containers[0]

meetingContainers = getSoup(myUrl + container.a["href"]).findAll("div", {"id" : "main-content"})

meetinghtml = getSoup(myUrl + meetingContainers[0].a["href"]) #all links send to same table meeting, just take the 1st one
meetingTable = meetinghtml.find("div", {"class" : "search-results"}).select("tr")[1:]

for meetingTopic in meetingTable :
    votingTopic = meetingTopic.select("td")[3].text.replace(',', '-')
    votingDate = meetingTopic.select("td")[4].text

    votingSoup = getSoup(myUrl + meetingTopic.a["href"])

    votingContent = votingSoup.find("div", {"id" : "main-content"})

    politParties = votingContent.find_all("h2", {"class" : "section-title center"})[1: - 1]
    politPartyNames = [party.text.split(" (")[0] for party in politParties]

    politPartiesVotes = votingContent.find_all("ul", {"class" : "results"})

    votes = zip(politPartyNames, politPartiesVotes)
    print(votingTopic)
    for i in votes:
        for personVote in i[1].find_all("li"):
            fVote.write(votingTopic + ',' +  votingDate + ',' + i[0] + ',' + personVote.a.text + ',' + personVote.span["class"][1] + '\n' )
        
    
    sleep(0.3)
