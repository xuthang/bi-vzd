encodingType = 'windows-1250'

old = open('meeting.csv', 'r', encoding='utf-8')
new = open('newMeeting.csv', 'w', encoding = encodingType)
new.write(old.read())
