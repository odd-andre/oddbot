import datetime
import random

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import youtube_dl

YDL_OPTIONS = {'format': 'bestaudio'}


class queueHandler():
    DEVELOPER_KEY = 'AIzaSyDD0yNTmif6hgUIZor1fNeo46u4VKDfVkE'
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'

    queue = {}
    state = {}
    loop = {}
    loopPos = {}
    currentlyPlaying = {}
    # 0: off 1: playing 2: paused

    def setup(self,guildId):
        self.state[guildId] = 0
        self.queue[guildId] = []

    def setState(self, newState, guildId):
        if guildId not in self.state.keys():
            self.state[guildId] = newState
        else:
            self.state[guildId] = newState

    def getState(self, guildId):
        if guildId not in self.state.keys():
            self.state[guildId] = 0

        return self.state[guildId]

    def getLoop(self,guildId):
        if guildId not in self.loop.keys():
            self.setLoop(guildId, 0)
        return self.loop[guildId]

    def setLoop(self,guildId,state):
        self.loop[guildId] = state

    def setLoopPos(self, guildId, pos):
        self.loopPos[guildId] = pos

    def getLoopPos(self,guildId):
        if guildId not in self.loopPos.keys():
            self.setLoopPos(guildId, 0)
        return self.loopPos[guildId]

    def getCurrentSongInfo(self,guildId):
        if guildId in self.currentlyPlaying.keys():
            return self.currentlyPlaying[guildId]['name']
        else:
            return 0

    def printQueue(self,guildId):
        count = 1
        totalSeconds = 0
        printQ = "```"
        if guildId in self.queue.keys() and len(self.queue[guildId]) > 0:
            for song in self.queue[guildId]:
                queueNr = count
                if count == 1:
                    queueNr = 'Next song:'
                if count < 26:
                    printQ = printQ+' '+str(queueNr)+' '+song['name']+'  Duration: '+str(datetime.timedelta(seconds=song['duration']))+'\n'
                totalSeconds += song['duration']
                count += 1
            if count > 25:
                printQ += '     and '+str(count-25)+' other songs...\n'
            printQ += '\n Total duration: '+str(datetime.timedelta(seconds=totalSeconds))
            printQ = printQ+"```"
            return printQ
        else:
            return 0

    def clearQueue(self, guildId):
        self.queue[guildId] = []


    def addToQueue(self, urlSent,guildId):
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(urlSent, download=False)
            if 'entries' in info.keys():
                for song in info['entries']:
                    songDict = {}
                    songDict['url'] = song['formats'][0]['url']
                    songDict['name'] = song['title']
                    songDict['duration'] = song['duration']

                    if guildId in self.queue.keys():
                        self.queue[guildId].append(songDict)
                    else:
                        self.queue[guildId] = []
                        self.queue[guildId].append(songDict)
            else:
                songDict = {}
                songDict['url'] = info['formats'][0]['url']
                songDict['name'] = info['title']
                songDict['duration'] = info['duration']
                if guildId in self.queue.keys():
                    self.queue[guildId].append(songDict)
                else:
                    self.queue[guildId] = []
                    self.queue[guildId].append(songDict)

    def nextInQueue(self, guildId):
        if guildId in self.queue.keys():
            if len(self.queue[guildId]) > 0:
                if self.getLoop(guildId) == 1:
                    nextQ = self.queue[guildId][self.getLoopPos(guildId)]['url']
                    if len(self.queue[guildId])-1 == self.getLoopPos(guildId):
                        self.setLoopPos(guildId, 0)
                    else:
                        curLoop = self.getLoopPos(guildId)
                        self.setLoopPos(guildId, curLoop+1)
                    self.currentlyPlaying[guildId] = self.queue[guildId][self.getLoopPos(guildId)]
                    return nextQ
                else:
                    nextQ = self.queue[guildId][0]['url']
                    self.currentlyPlaying[guildId] = self.queue[guildId][0]
                    self.queue[guildId].pop(0)
                    return nextQ
            else:
                self.setState(0, guildId)
                return 0
        else:
            self.setState(0, guildId)
            return 0

    def shufflePlaylist(self,guildId):
        random.shuffle(self.queue[guildId])

    def removeFromQueue(self,guildId,nr):
        if nr < len(self.queue[guildId]):
            self.queue[guildId].pop(nr-1)

    def getCurrent(self,guildId):
        if guildId in self.currentlyPlaying.keys():
            return self.currentlyPlaying[guildId]
        else:
            return 0

    def searchYoutube(self,search):
        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.DEVELOPER_KEY)

        search_response = youtube.search().list(
            q=search,
            part='snippet',
            maxResults=10,
        ).execute()
        videos = []
        playlists = []
        channels = []
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                videos.append('%s' % (search_result['id']['videoId']))
            elif search_result['id']['kind'] == 'youtube#channel':
                channels.append('%s' % (search_result['id']['channelId']))
            elif search_result['id']['kind'] == 'youtube#playlist':
                playlists.append('%s' % (search_result['id']['playlistId']))
        test = 0
        return 'test'
