import usys as sys
sys.path.append('') # See: https://github.com/micropython/micropython/issues/6419

import lvgl as lv
import meta

import uos
import imagetools 


lv.init()

# Register display driver.

WIDTH_SCREEN = 1200
WIDTH = WIDTH_SCREEN
HEIGHT_SCREEN = 800 
HEIGHT = HEIGHT_SCREEN
IMAGE_HOME = 'carton1.jpg'

# PC configuration
#from config import config
# embedded
import meta

if meta.PLATFORM == "lpi":
    from configlpi import config
elif meta.PLATFORM == "lpiinternal":
    from configlpiinternal import config
elif meta.PLATFORM == "":
    from config import config
elif meta.PLATFORM == "vm":
    from configvm import config
else:
    raise Exception("unknown meta.PLATEFORM " + str(meta.PLATFORM))


conf = config()

# display memory
import micropython
print(micropython.mem_info(1))


disp_buf1 = lv.disp_draw_buf_t()
buf1_1 = bytearray(WIDTH_SCREEN*10)
buf1_2 = bytearray(WIDTH_SCREEN*10)
disp_buf1.init(buf1_1, buf1_2, len(buf1_1)//4)
disp_drv = lv.disp_drv_t()
disp_drv.init()
disp_drv.draw_buf = disp_buf1
disp_drv.flush_cb = conf.cb
disp_drv.hor_res = WIDTH_SCREEN
disp_drv.ver_res = HEIGHT_SCREEN

if meta.INVERTED_SCREEN:
    disp_drv.sw_rotate = 1 
    disp_drv.rotated = lv.DISP_ROT._180

disp = disp_drv.register()

decoder = lv.img.decoder_create()
decoder.info_cb = imagetools.get_png_info
decoder.open_cb = imagetools.open_png



def create_panel(obj):
    """ 
       create a container panel 
    """
    panel = lv.obj(obj)
    cur_theme = lv.theme_default_get()
    default_color = lv.style_prop_get_default(lv.STYLE.BG_COLOR).color
    # print(default_color.color_to32())
    panel.set_style_bg_opa(lv.OPA.TRANSP, 0)
    panel.set_style_border_opa(lv.OPA.TRANSP, 0)

    return panel


def reset_margins(obj):
    obj.set_style_pad_top(0, lv.PART.MAIN)
    obj.set_style_pad_left(0, lv.PART.MAIN)
    obj.set_style_pad_right(0, lv.PART.MAIN)
    obj.set_style_pad_bottom(0, lv.PART.MAIN)


def margins(obj, left = 0, right = 0, top = 0, bottom = 0):
    obj.set_style_pad_top(top, lv.PART.MAIN)
    obj.set_style_pad_left(left, lv.PART.MAIN)
    obj.set_style_pad_right(right, lv.PART.MAIN)
    obj.set_style_pad_bottom(bottom, lv.PART.MAIN)


# model
class PlayElement:

    def __init__(self, name, filename, length, index = 0):
        self.name = name
        self.filename = filename
        self.length = length
        self.index = index

    def constructFromFile(directory, filename, index):
        o = PlayElement(filename[0:-4], filename, -1, index)
        o.filepath = directory
        return o

    def fullpath(self):
        if self.filepath:
            return self.filepath + "/" + self.filename
        return self.filename

class Screen:
    def __init__(self, parent, eventbus):
        self.parent = parent
        assert parent is not None
        self.eventbus = eventbus
        eventbus.subscribe(self)
        assert eventbus is not None
        self.scr = self.construct(parent)
        assert self.scr != None

    def construct(self, parent):
        raise Exception("construct method must be overloaded in base class")

    def receiveEvent(self, event):
        pass

    def dispatchEvent(self, event):
        self.eventbus.dispatchOthers(event, self)


class EventBus:
    def __init__(self):
        self.subscribers = []

    def dispatch(self, event):
        for i in self.subscribers:
            i.receiveEvent(event)

    def dispatchOthers(self, event, sender):
        # print("sending " + str(event))
        for i in self.subscribers:
            if i != sender:
                i.receiveEvent(event)

    def subscribe(self, subscriber):
        if subscriber is not None:
            self.subscribers.append(subscriber)


AUTHORIZED_EXTENSIONS = [ ".mid", ".midi", ".MID", ".midx", ".MIDX", ".midix",
                     ".kar", ".KAR", ".karx", ".KARX", ".book", ".bookx"]


class FileExplorer:
    """
        File exploring helper, business containing the file list
        and managing the walk into library
    """

    def __init__(self, mainpath):
        if mainpath is None:
            mainpath = "."
        self.mainpath = mainpath
        self.paths = []

    def fullpath(self):
        p = self.mainpath + "/" + "/".join(self.paths)
        return p

    def list_files(self):
       
        try:
            p = self.fullpath()
            l = []
            for t in uos.ilistdir(p):
                (name,t,inode) = t
                if name != "." and name != "..":
                    if name[-4:] in AUTHORIZED_EXTENSIONS or name[-5:] in AUTHORIZED_EXTENSIONS:
                        l.append(name)
                    # add directories
                    # print(name + " t : " + str(t))
                    if (t & 0x4000) != 0:
                        l.append(name)
        except:
            pass   

        # sort the element
        l.sort()
        return l 

    def isDirectory(self, filename):
        try:
            p = self.fullpath()
            l = []
            for t in uos.ilistdir(p):
                (name,t,inode) = t
                if filename == name:
                    return (t & 0x4000) != 0
        except:
            pass   

        # sort the element
       
        return False

    def up(self):
        if len(self.paths) > 0:
            self.paths = self.paths[0:-1]

    def root(self):
        self.paths = []

    def go(self, subpath):
        if subpath is not None:
            self.paths.append(subpath)
