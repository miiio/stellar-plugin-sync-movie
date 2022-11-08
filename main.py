import StellarPlayer
import asyncio
from .websockets import client
import json
class SynClient():
    def __init__(self, player, address=None):
        self.loop = asyncio.new_event_loop()
        self.player = player
        self.address = address
        asyncio.set_event_loop(self.loop)     
    
    def connect(self, address=None):
        if address is not None:
            self.address = address
        self.loop.run_until_complete(self.clientRun())
    
    async def clientRun(self):
        async with client.connect(self.address) as websocket:
            await self.recvMessage(websocket)
            
    async def recvMessage(self, websocket):
        while True:
            recv_text = await websocket.recv()
            if recv_text == 'ping':
                await websocket.send("pong")
                continue
            print("recv:" + recv_text)
            self.resultHandler(recv_text)
            
    def resultHandler(self, result):
        if result is None: return
        obj = None
        try:
            obj = json.loads(result)
        finally:
            if obj == None: return
        if "action" not in obj: return
        print("action:" + obj["action"])
        if obj["action"] == 'play':
            self.player.pause(False)
        elif obj["action"] == 'pause':
            self.player.pause(True)
        elif obj["action"] == 'seek':
            print("self.player.seek")
        elif obj["action"] == 'change_rate':
            print("self.player.change_rate")
class myplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        StellarPlayer.IStellarPlayerPlugin.__init__(self, player)
        
    def stop(self):
        return super().stop()

    def start(self):     
        return super().start()
        
    def show(self):
        controls = [[{"type": "edit", "name": "address", "width":400, "height":50}, {"type": "button", "name": "connect", "width":50, "height":50}]]
        self.doModal('main',600, 80,'连接服务器', controls)
    
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = myplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
