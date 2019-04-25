import paho.mqtt.client as mqtt
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.app import App

class BingoMain(Widget):

    listOfLastBalls= []

    global partyColor
    partyColor = []
    for i in range(11):
        partyColor.append(1)
    partyColor[0] = (0, 0, 0, 1)
    partyColor[1] = (1, .8, .4, 1)
    partyColor[2] = (1, 1, 1, 1)
    partyColor[3] = (1, 1, 0, 1)
    partyColor[4] = (0, .4, 1, 1)
    partyColor[5] = (1, .2, .8, 1)
    partyColor[6] = (0, 1, 0, 1)
    partyColor[7] = (1, .6, 1, 1)
    partyColor[8] = (0, 0, 1, 1)
    partyColor[9] = (1, .4, 0, 1)
    partyColor[10] = (1, 0, 0, 1)

    def build(self):
        self.partyTouched("1")

    def callback(self, *args):
        print("callback for new test")

    def btnTouched(self,  myText):
        self.listOfLastBalls.append(myText)
        App.get_running_app().cli.publish("game/balls", myText)

    def partyTouched(self, idParty):
        self.rgbFrame = partyColor[int(idParty)]
        App.get_running_app().cli.publish("game/party", idParty)


    def update(self, time):
        pass

    def resetGame(self, idParty):
        for i in range(1,91):
            currentButton="button"+str(i)
            self.ids[currentButton].background_color = .4, .4, .4, 1
            self.ids[currentButton].color = 1, 1, 1, 1
        self.rgbFrame = partyColor[int(idParty)]
        self.ids['mainFrame'].text = "DEFI {0}".format(idParty)
        self.ids['ongoingParty'].text = "Partie en cours : DEFI MONTAGNARD {0}".format(idParty)

    def updateButton(self,cli, msg,listOfLastBalls):
        if self.ids[msg].background_color==[.4,.4,.4,1]:
            self.ids[msg].background_color = 0, 1, 0, 1
            self.ids[msg].color=0,0,0,1
        else:
            self.ids[msg].background_color = .4, .4, .4, 1
            self.ids[msg].color = 1, 1, 1, 1
        self.ids['mainFrame'].text = str(listOfLastBalls[-1])



class Bingo2App(App):

    listOfLastBalls=[]

    cli = mqtt.Client(protocol=mqtt.MQTTv311)
    myApp = Widget()
    def build(self):
        app=BingoMain()
        self.myApp=app
        Clock.schedule_interval(app.update, 1)
        return app

    def on_start(self):
        print("trying to connect")
        self.cli.on_connect = self.on_connect
        self.cli.on_message = self.on_message
        self.cli.connect('test.mosquitto.org', port=1883, keepalive=60)
        self.cli.loop_start()

    def on_connect(self, client, userdata, flags, respons_code):
        client.subscribe('game/balls')
        client.subscribe('game/party')

    def on_message(self, client, userdata, msg):
        msg.payload = msg.payload.decode("utf-8")

        if msg.topic == "game/balls":
            print("last element : {0}".format(str(self.listOfLastBalls[-1:])))
            print("reçu : {0}".format(msg.payload))
            if msg.payload in self.listOfLastBalls:
                print("c'est le même")
                self.listOfLastBalls.pop()
                self.listOfLastBalls.pop()
            self.listOfLastBalls.append(msg.payload)
            print(self.listOfLastBalls)
            self.myApp.updateButton(self.cli, "button{0}".format(msg.payload), self.listOfLastBalls)
        elif msg.topic == "game/party":
            print("Party reset - game {0}".format(msg.payload))
            self.myApp.resetGame("{0}".format(msg.payload))
            self.listOfLastBalls.clear()
            print(msg)
        else:
            print("J'ai rien compris")


if __name__ == '__main__':
    Bingo2App().run()




