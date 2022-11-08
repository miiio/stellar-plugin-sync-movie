import StellarPlayer

class myplugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self,player:StellarPlayer.IStellarPlayer):
        StellarPlayer.IStellarPlayerPlugin.__init__(self, player)             
        
    def stop(self):
        return super().stop()

    def start(self):      
        return super().start()
        
    def show(self):
        self.doModal('main',300, 300,'测试', [
			{'type':'label','name':'hello', 'hAlign': 'center'}
        ])

    
def newPlugin(player:StellarPlayer.IStellarPlayer,*arg):
    plugin = myplugin(player)
    return plugin

def destroyPlugin(plugin:StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
