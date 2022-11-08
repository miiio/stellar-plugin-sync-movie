import asyncio
import websockets
import json

IP_ADDR = "127.0.0.1"
IP_PORT = "9000"

class myplugin():
    def __init__(self):
        pass         
        
    def stop(self):
        pass

    def start(self):     
        print("======client main begin======")
        asyncio.get_event_loop().run_until_complete(self.clientRun())
        pass
    
    def resultHandler(self, result):
        if result is None: return
        obj = None
        try:
            json.loads(result)
        finally:
            if obj == None: return
        
        if "action" not in obj: return
        if obj["action"] == 'play':
            
            pass
        elif obj["action"] == 'pause':
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
        async with websockets.connect("ws://" + ipaddress) as websocket:
            await self.recvMessage(websocket)

if __name__ == '__main__':
    plugin = myplugin()
    plugin.start()

# switch (result.action) {
#     default:
#         this.pause();
#         break;
#     case 'play':
#         this.seekTime = [result.time];
#         this.updateVideoCurrentTime(result.time);
#         this.play();
#         break;
#     case 'pause':
#         this.seekTime = [result.time];
#         this.updateVideoCurrentTime(result.time);
#         this.pause();
#         break;
#     case 'seek':
#         this.seekTime = [result.time];
#         this.updateVideoCurrentTime(result.time);
#         break;
#     case 'change_rate':
#         this.seekTime = [result.time];
#         this.updateVideoCurrentTime(result.time);
#         this.$store.dispatch(videoActions.CHANGE_RATE, result.rate);
#         this.nowRate = result.rate;
#         break;
# }