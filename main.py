import StellarPlayer
import asyncio
from .websocket import create_connection
import json
import threading
import time

import os


class SynClient():
    def __init__(self, player, plugin):
        self.loop = asyncio.new_event_loop()
        self.player = player
        self.plugin = plugin
        self.address = None
        self.room = None
        self.ws = None
        self.connected = False
        self.delay = 0
        asyncio.set_event_loop(self.loop)
        
    def sendCMD(self, data, delay=False):
        if not self.connected: return
        data['room'] = self.room if self.room is not None else ""
        if "pos" in data and delay:
            data["pos"] += self.delay + 1000
        self.ws.send(json.dumps(data))
        
    def connect(self, address=None, room=None):
        if address is not None: self.address = address
        if room is not None: self.room = room
        self.connected = False
        try:
            self.ws = create_connection(self.address)
        except Exception as err:
            self.plugin.onConnectFail(str(err))
        finally:
            pass
        t = threading.Thread(target=self.wsThread, daemon=True)
        t.start()
        
    def disconnect(self):
        if not self.connected: return
        self.ws.close()
        self.connected = False
        
    def testDelay(self, n):
        if not self.connected: return
        import time
        dCnt = 0
        for i in range(n):
            timestamp = (int)(time.time()*1000)
            pong = "pong" + str(timestamp)
            # print("test ping " + pong)
            self.ws.send("ping" + str(timestamp))
            recv = ""
            tryCnt = 0
            while tryCnt < 5:
                tryCnt += 1
                recv = self.ws.recv()
                if recv != pong:
                    continue
                else:
                    break
            now = ((int)(time.time()*1000))
            d = now - timestamp
            print("test ping" + str(i) + ":" + str(d))
            dCnt += d
        
        self.delay = (int)(dCnt / n / 2)
    
    def wsThread(self):
        self.connected = True
        
        self.delay = 0
        self.testDelay(5)
        
        self.plugin.onConnectSuccess()
        while self.connected:
            recv = None
            try:
                recv = self.ws.recv()
            except Exception as err:
                self.ws.close()
                if self.connected:
                    self.plugin.onConnectFail(str(err))
                else:
                    self.plugin.onDisConnectSuccess()
                self.connected = False
                return
            finally:
                pass
            
            if recv is None: continue
            if recv == 'ping':
                self.ws.send("pong")
                continue
            self.resultHandler(recv)
            
        self.plugin.onDisConnectSuccess()
            
            
    def resultHandler(self, result):
        if result is None: return
        obj = None
        try:
            obj = json.loads(result)
        finally:
            if obj == None: return
            
        if "room" not in obj or (self.room is not None and obj['room'] != self.room):
            return
            
        if "action" not in obj: return
        print("action:" + obj["action"])
        try:
            if obj["action"] == 'play':
                self.pause(False)
                self.setProgress(int(obj["pos"]), True)
            elif obj["action"] == 'pause':
                self.pause(True)
                self.setProgress(int(obj["pos"]))
            elif obj["action"] == 'seek':
                self.setProgress(int(obj["pos"]), True)
        except Exception as e:
            print(e)
        finally:
            pass
    
    def setProgress(self, p, delay=False):
        if delay:
            p += self.delay
        self.plugin.seekFlag = True
        self.player.setProgress((p+500)//1000)
        
    def pause(self, b, delay=False):
        _status = self.player.getPlayInfo()['status']
        if _status != 0 and _status != 1:
            return
        
        self.plugin.pauseFlag = True
        if _status == 0 and b or _status == 1 and not b:
            self.player.pause(b)
            
class myplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        StellarPlayer.IStellarPlayerPlugin.__init__(self, player)
        self.synClient = SynClient(self.player, self)
        self.lastProgress = -1
        # self.address = "ws://127.0.0.1:9000"
        self.address = "wss://service-q4m0ngg6-1253081785.gz.apigw.tencentcs.com/release/"
        self.room = ""
        self.status = "等待连接"
        self.connect_btn = "connect"
        self.pageId = "sync-movie"
        self.seekFlag = False
        self.pauseFlag = False
        self.reTry = True
        self.reTryCount = 0
        self.MaxreTryCount = 5
        self.reTryDelay = 3000
        
        
    def get_methods(self):
        return (list(filter(lambda m: not m.startswith("_") and callable(getattr(self, m)),
                        dir(self))))
        
    #['doModal', 'get_methods', 'handleRequest', 'onClick', 'onClickAdvert', 'onEditInput', 'onFastBackward', 'onFastForward', 'onListItemControlClick', 'onListItemDblClick'
    # , 'onModalCreated', 'onPause', 'onPlay', 'onPlayerSearch', 'onProgress', 'onRunning', 'onStopPlay', 'onUrlInput', 'onVideoRendered', 'processTemplate'
    # , 'show', 'start', 'stop', 'updateLayout']
    def onPause(self, *args):  
        # play=0 暂停; play=1 继续
        if self.pauseFlag:
            self.pauseFlag = False
            return
        print("onPause:" + str(args))
        s, p, _ = args
        pos = self.player.getProgress()[0] * 1000
        if s == 0:
            self.synClient.sendCMD({
                "action": "pause",
                "pos": pos
            }, False)
        elif s == 1:
            self.synClient.sendCMD({
                "action": "play",
                "pos": pos
            }, True)
    
    def onFastBackward(self, *args):
        print("onFastBackward:" + str(args))
        
    def onFastForward(self, *args):
        print("onFastForward:" + str(args))
        
    def onPlay(self, *args):
        print("onPlay:" + str(args))
        
    def onClick(self, *args):
        print("onClick:" + str(args))
        
    def handleRequest(self, *args):
        print("handleRequest:" + str(args))
        
    def onSeek(self, pos):
        if self.seekFlag:
            self.seekFlag = False
            return
        print("onSeek:" + str(pos))
        self.synClient.sendCMD({
            "action": "seek",
            "pos": pos
        })
        
    def onProgress(self, *args):
        p, _ = args
        
        if self.lastProgress == -1:
            self.lastProgress = p
            return
        
        if abs(p - self.lastProgress) > 1100:
            self.onSeek(p)
        self.lastProgress = p
        # print("onProgress:" + str(args))
        
    
    def stop(self):
        self.synClient.disconnect()
        return super().stop()

    def start(self):     
        print(self.get_methods())
        return super().start()
    
    def handleConnect(self, *args):
        if self.synClient.connected: return
        print(self.address + "," + self.room)
        self.player.showControl(self.pageId, "connect", False)
        self.status = "正在连接..."
        self.reTryCount = 0
        self.synClient.connect(self.address, self.room)
        
    def handleDisConnect(self, *args):
        if not self.synClient.connected: return
        print("handleDisConnect")
        self.player.showControl(self.pageId, "disConnect", False)
        self.status = "正在断开连接..."
        self.synClient.disconnect()
        
        
    def show(self):
        controls = [
            {"type": "space", "height":0.1},
            [{'type':'space', "width":30},{"type": "label", "name": "status", "width":60},{"type": "label", "name": "等待连接","width":230, ":value":"status"}, {"type": "button", "name": "connect", "width":100, '@click': 'handleConnect'}, {"type": "button", "name": "disconnect", "width":0, '@click': 'handleDisConnect'},{'type':'space', "width":25}],
            {"type": "space", "height":0.1},
            [{'type':'space', "width":25},{"type": "edit", "name": "address", "width":400, ":value": "address"}],
            {"type": "space", "height":0.1},
            [{'type':'space', "width":40},{"type": "edit", "name": "room", "width":385, ":value": "room"}],
            {"type": "space", "height":0.1},
        ]
        self.doModal(self.pageId,440, 180,'连接服务器', controls)
        self.player.showControl(self.pageId, "disconnect", False)
        
    def onConnectSuccess(self):
        self.status = "已连接, ping:" + str(self.synClient.delay) + "ms"
        self.player.showControl(self.pageId, "connect", False)
        self.player.setControlSize(self.pageId, "disconnect", width=100)
        self.player.showControl(self.pageId, "disconnect", True)
        
    def onConnectFail(self, err):
        self.status = "连接失败:" + (str(err) if err is not None else "None")
        self.player.showControl(self.pageId, "connect", True)
        self.player.showControl(self.pageId, "disconnect", False)
        
        if self.reTry:
            t = threading.Thread(target=self.wsThread, daemon=True)
            t.start()
        
    def reTryThread(self):
        if not self.reTry or self.synClient.connected: return
        self.reTryCount += 1
        if self.reTryCount > self.MaxreTryCount:
            self.status = "重连次数已达最大值,请检查服务器状态."
            return
        time.sleep(self.reTryDelay / 1000)
        
        
        print("retry: " + self.address + "," + self.room)
        self.player.showControl(self.pageId, "connect", False)
        self.status = "正在尝试第" + str(self.reTryCount) + "重连..."
        self.synClient.connect(self.address, self.room)
        
        
    def onDisConnectSuccess(self):
        self.status = "等待连接"
        self.player.showControl(self.pageId, "connect", True)
        self.player.showControl(self.pageId, "disconnect", False)
        self.reTryCount = 0
    
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = myplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
