
import meta
import SDL
import lvgl as lv

class avancement:

    def __init__(self):
        self.f = open("/dev/ttyACM0")
        print("opened tty")
        self.pos = None
        self.increments = 0
        self.globalposition = 0
        self.buffer = ""
    def loop(self):
        linesstring = self.f.read()
        #print(linesstring)
        self.buffer = self.buffer + linesstring + "\n"
        #print(" len" + str(len(self.buffer)))
        while self.buffer.find("\n") != -1:
            i = self.buffer.find("\n")
            v = self.buffer[0:i]
            self.buffer = self.buffer[i+1:]
            if i == 0:
                continue
            if v == "":
                continue
            ipos = int(v)
            #print("position :" + str(ipos))
            self.handle(ipos)

    def handle(self, position):
        if self.pos is None:
            self.pos = position
            return
        oldpos = self.pos
        oldquadrant = oldpos/(4096 >> 2)
        newquadrant = position/(4096 >> 2)
        if newquadrant - oldquadrant < -2:
            position = position + 4096
        elif newquadrant - oldquadrant > 2:
            # reverse
            oldpos = +oldpos + (4096 - position) + position
        increment = position - oldpos
        self.globalposition += increment
        self.increments += increment
        self.pos = position % 4096

    def readIncrement(self):
        retvalue = self.increments
        if retvalue > 500:
            retvalue = 0
        self.increments = 0
        return retvalue



class config:

    def __init__(self):

        SDL.init(w=1200,h=800)
        self.cb = SDL.monitor_flush
        # manivelle 
        #self.avancement = avancement()

        self.FILE_DIRECTORY = "../mpy-orgue/files"
        self.calibration = [0,800,0,480]


    def install(self):

        indev_drv = lv.indev_drv_t()
        indev_drv.init() 
        indev_drv.type = lv.INDEV_TYPE.POINTER;
        indev_drv.read_cb = SDL.mouse_read;
        indev_drv.register();
        self.indev_drv = indev_drv

    def configure(self, midiplayer):        
        #midiplayer.property_set("sound_path", "../sons_lt/")
        midiplayer.property_set("sound_path", "../sons/")
        # midiplayer.property_set("output_serial_device", "/dev/pts/21")
                                                       
        midiplayer.init()                   

    def set_automatic_play(self, value):
        pass   

    def calibration_get(self):
        return self.calibration
        
    def calibration_set(self, list):
        self.calibration = list
    
    def calibration_del(self):
        pass

