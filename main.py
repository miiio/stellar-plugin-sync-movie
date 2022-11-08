import StellarPlayer
import asyncio
from .websockets import client
import json

IP_ADDR = "127.0.0.1"
IP_PORT = "9000"

class myplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        StellarPlayer.IStellarPlayerPlugin.__init__(self, player)        
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)     
        
    def stop(self):
        return super().stop()

    def start(self):     
        print("======client main begin======")
        self.loop.run_until_complete(self.clientRun())
        return super().start()
        
    def show(self):
        self.doModal('main',300, 300,'测试22', [
			{'type':'label','name':'hello222', 'hAlign': 'center'}
        ])

    def resultHandler(self, result):
        if result is None: return
        obj = None
        try:
            json.loads(result)
        finally:
            if obj == None: return
        
        if "action" not in obj: return
        print("action:" + obj["action"])
        if obj["action"] == 'play':
            self.player.pause(False)
            pass
        elif obj["action"] == 'pause':
            self.player.pause(True)
            pass
        elif obj["action"] == 'seek':
            pass
        elif obj["action"] == 'change_rate':
            pass
        
    
    async def recvMessage(self, websocket):
        while True:
            recv_text = await websocket.recv()
            if recv_text == 'ping':
                await websocket.send("pong")
                continue
            print("recv_text:" + recv_text)
            self.resultHandler(recv_text)
            

    # 进行websocket连接
    async def clientRun(self):
        ipaddress = IP_ADDR + ":" + IP_PORT
        async with client.connect("ws://" + ipaddress) as websocket:
            await self.recvMessage(websocket)
    
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = myplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
