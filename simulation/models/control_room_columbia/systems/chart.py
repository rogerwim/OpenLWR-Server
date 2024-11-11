from simulation.models.control_room_columbia import model
from simulation.models.control_room_columbia.reactor_physics import reactor_inventory
from simulation.models.control_room_columbia.reactor_physics import pressure

class RecorderDX1000:
    def __init__(self,name):
        self.name = name
        self.channels = {}
        self.channel_alarms = {}
        self.allow_reprogram = False
        self.sampling_enabled = False #Disables drawing of graphs

        self.page = 1

        self.buttons = {
            "ENTER" : False, #ENTER/DISP
            "LEFTARROW" : False,
            "RIGHTARROW" : False,
            "UPARROW" : False,
            "DOWNARROW" : False,
            "MENU" : False,
            "ESCAPE" : False,
        }
        self.buttons_pressed = {
            "ENTER" : False, #ENTER/DISP
            "LEFTARROW" : False,
            "RIGHTARROW" : False,
            "UPARROW" : False,
            "DOWNARROW" : False,
            "MENU" : False,
            "ESCAPE" : False,
        }
        self.elements = { #additional stuff on screen that isnt a page change
            "MODE_SELECT":{
                "SEL":1,
                "SHOW":False,
            },
        } 

        model.recorders[self.name] = self

    def set_allow_reprogram(self,allow):
        self.allow_reprogram = allow

    def add_channel(self,channel_name,unit,initial_value=0,low_over=0,over=0):
        self.channels[channel_name] = {"text":str(initial_value),"unit":unit,"value":initial_value,"+over":over,"-over":low_over}

    def bind_alarm(self,channel_name,alarm_type,limit,hysteresis):
        self.channel_alarms[channel_name] = {"alarm_type":alarm_type,"limit":limit,"hysteresis":hysteresis}

    def set_channel_value(self,channel_name,value):
        self.channels[channel_name]["value"] = value

    def button_updated(self,button,state):
        if button in self.buttons:
            self.buttons[button] = state

    def calculate(self):
        for channel in self.channels:
            channel = self.channels[channel]
            if channel["value"] > channel["+over"]:
                channel["text"] = "+Over"
            elif channel["value"] < channel["-over"]:
                channel["text"] = "-Over"
            else:
                channel["text"] = str(round(channel["value"],3))

        #buttons

        if self.buttons["ENTER"] and not self.buttons_pressed["ENTER"]:
            #if we're on the normal value pages, open the selection box to go to another
            if (self.page == 1 or self.page == 2) and not self.elements["MODE_SELECT"]["SHOW"]:
                self.elements["MODE_SELECT"]["SHOW"] = True
            elif self.elements["MODE_SELECT"]["SHOW"] and (self.page == 1 or self.page == 2):
                self.elements["MODE_SELECT"]["SHOW"] = False
                self.page = self.elements["MODE_SELECT"]["SEL"]

        if self.buttons["MENU"] and not self.buttons_pressed["MENU"]:

            #any value display page to settings page
            if self.page == 1 or self.page == 2:
                self.page = 3

        if self.buttons["ESCAPE"] and not self.buttons_pressed["ESCAPE"]:

            #menu page back to regular
            #TODO: save the view selected
            if self.page == 3:
                self.page = 1

        for button in self.buttons:
            if self.buttons[button]:
                self.buttons_pressed[button] = True
            else:
                self.buttons_pressed[button] = False

    def change_page(self,page):
        self.page = page

    #TODO: Alarms

    #TODO: Trend


def initialize():
    a = RecorderDX1000("601RPV")
    a.add_channel("RPV LEVEL WR","INCHES",0,-150,60)
    a.add_channel("RPV PRESS","PSIG",0,0,5000)

    a = RecorderDX1000("601FZR")
    a.add_channel("FUEL ZONE LEVEL","INCHES",-110,-300,-110)
    a.add_channel("FUEL ZONE COMP","INCHES",-110,-300,-110)

    a = RecorderDX1000("601WWP")
    a.add_channel("WETWELL PRESSURE","PSIG",0,-10,100) #find proper ranges

    a = RecorderDX1000("601DWP1")
    a.add_channel("DRYWELL RANGE 1","PSIG",0,-5,3)
    a.add_channel("DRYWELL RANGE 2","PSIG",0,0,25)
    a.add_channel("DRYWELL RANGE 3","PSIG",0,0,180)


def run():
    model.recorders["601RPV"].channels["RPV LEVEL WR"]["value"] = reactor_inventory.rx_level_wr
    model.recorders["601RPV"].channels["RPV PRESS"]["value"] = pressure.Pressures["Vessel"]/6895

    model.recorders["601FZR"].channels["FUEL ZONE LEVEL"]["value"] = reactor_inventory.rx_level_fzr
    model.recorders["601FZR"].channels["FUEL ZONE COMP"]["value"] = reactor_inventory.rx_level_fzr #apparently compensated so it works at all pressures?

    model.recorders["601WWP"].channels["WETWELL PRESSURE"]["value"] = -11 #intentionally -Over

    model.recorders["601DWP1"].channels["DRYWELL RANGE 1"]["value"] = round(pressure.Pressures["Drywell"]/6895,2)
    model.recorders["601DWP1"].channels["DRYWELL RANGE 2"]["value"] = round(pressure.Pressures["Drywell"]/6895,2)
    model.recorders["601DWP1"].channels["DRYWELL RANGE 3"]["value"] = round(pressure.Pressures["Drywell"]/6895,2)

    for recorder in model.recorders:
        model.recorders[recorder].calculate()
