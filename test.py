import asyncio
import websockets
import json

IP_ADDR = "ws://127.0.0.1:9000"

class SynClient():
    def __init__(self, player, address=None):
        self.loop = asyncio.new_event_loop()
        self.player = player
        self.address = address
        self.ws = None
        self.connected = False
        asyncio.set_event_loop(self.loop)     
    
    def connect(self, address=None):
        if address is not None:
            self.address = address
        self.loop.run_until_complete(self.clientRun())
        
    
    def disconnect(self):
        self.connected = False
        print("close...")
        # self.loop.run_until_complete(self.asyncDisconnect())
        
    async def asyncDisconnect(self):
        await self.ws.close()
        self.connected = False
    
    async def clientRun(self):
        try:
            self.ws = await websockets.connect(self.address)
            await self.recvMessage(self.ws)
        except Exception as e:
            print(e)
        finally:
            pass
            
    async def recvMessage(self, websocket):
        self.connected = True
        while True:
            if self.connected == False:
                websocket.close()
                return
            try:
                recv_text = await websocket.recv()
                print("recv:" + recv_text)
            except Exception as err:
                print(err)
                self.connected = False
            finally:
                pass
            if recv_text == 'ping':
                await websocket.send("pong")
                continue
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
            print("self.player.pause(False)")
        elif obj["action"] == 'pause':
            print("self.player.pause(True)")
        elif obj["action"] == 'seek':
            print("self.player.seek")
        elif obj["action"] == 'change_rate':
            print("self.player.change_rate")
        
    
import time
            
synClient = SynClient(None)

print("close...")
synClient.connect(IP_ADDR)
print("close...")

time.sleep(3000)

synClient.disconnect()