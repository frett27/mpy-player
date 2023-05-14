
import meta
from meta import I18N

# this import initialize the proper plateform, 
# and gives the needed functions for creating the application
from app import *

import lvgl as lv
import midiplayer
import utime
import uos
import os


import search

DEFAULT_FONT = lv.montserrat_latin_30
DEFAULT_FONT_BOLD = lv.montserrat_latin_bold_30
FONT_LYRICS= lv.montserrat_latin_bold_32
LIGHT_TEXT = lv.font_montserrat_14


BUTTON_MIN_HEIGHT = 70

JEU_AUTOMATIQUE = True

AUTOMATIC_CONTINUE = False
    

#LV_THEME_DEFAULT_COLOR_PRIMARY=lv.color_hex(0x249138) # green
#LV_THEME_DEFAULT_COLOR_SECONDARY=lv.color_hex(0xff5733)

#LV_THEME_DEFAULT_COLOR_PRIMARY=lv.color_hex(0x3b5998) # blue ambiance
#LV_THEME_DEFAULT_COLOR_SECONDARY=lv.color_hex(0x8b9dc3)

LV_THEME_DEFAULT_COLOR_PRIMARY=lv.color_hex(0x93441A) # brun ambiance
LV_THEME_DEFAULT_COLOR_SECONDARY=lv.color_hex(0xCA7C5C)



# create screen
GLOBAL_SCREEN = lv.obj()

# by default, set the font to 22
# scr.set_style_text_font(lv.font_montserrat_22, lv.STATE.DEFAULT)

GLOBAL_SCREEN.set_style_text_font(DEFAULT_FONT, lv.STATE.DEFAULT)




#    Create a palette of 8 colors:
#
#    primary: in LittlevGL for buttons, slider indicators, window headers
#    primary text: text on primary color
#    secondary: in LittlevGL for toggled buttons
#    secondary text: text on secondary color
#    surface: in LittlevGL for keyboard buttons, message box background
#    surface text: text on surface color
#    background: in LittlevGL screen, window etc. background
#    background text: text on background color
#
#    Update a theme (e.g. lv_theme_material) to use the colors from the palette.
#
#    Test the result with lv_test_theme1.
#


class Player:
    """
        Player object, maintain
    """

    def __init__(self):
        print("set property sound path to")
        
        # plateform specific initialization
        conf.configure(midiplayer)
      
        self.play_mode = False
        self.automatic_play = not JEU_AUTOMATIQUE

        # tempo for both automatic or not
        self.tempo = { True: 1.0, False: 1.0}

        self.set_automatic_play(True)
        self.set_automatic_play(JEU_AUTOMATIQUE)


    def play(self, play_element):

        midiplayer.stop()

        self.file_element = play_element
        midiplayer.play(play_element.fullpath())

        #print("length :" + str(midiplayer.playstreamlength()))
        #print("position :" + str(midiplayer.playstreamposition()))
        
        self.set_play_mode(True)

    def isPlaying(self):
        return midiplayer.isplaying() == 1

    def changeTempo(self, tempo):
        return midiplayer.changetempofactor(tempo)

    def changeTempoAuto(self, tempo, isAutomatic = True):
        self.tempo[isAutomatic] = tempo
        if self.automatic_play == isAutomatic:
            midiplayer.changetempofactor(tempo)
        

    def changePitch(self, pitch):
        return midiplayer.change_pitch(pitch)

    def set_play_mode(self, isPlaying = True):
        self.play_mode = isPlaying

    def set_automatic_play(self, auto):
        if self.automatic_play == auto:
            print("skip")
            return
        conf.set_automatic_play(auto)
        self.changeTempo(self.tempo[auto])
        self.automatic_play = auto


    def stop(self):
        if self.play_mode:
            self.set_play_mode(False)
            midiplayer.pauseresume()
            midiplayer.stopallvoices()

    def pause_resume(self):
        self.set_play_mode(not self.play_mode)
        midiplayer.pauseresume()
        midiplayer.stopallvoices()


    def current(self):
        if self.filename != None:
            return self.filename
        return ""

    def listdirs(self):
        return [FILE_DIRECTORY]

    def listElementsInDir(self,filepath):
        l = []
        for t in uos.ilistdir(filepath):
            (name,t,inode) = t
            if name[-4:] == ".mid":
                print(name)
                l.append(PlayElement.constructFromFile(filepath, name))
        return l

    
player = Player()

###########################################################################
# messages

class GoToExplore:
    def __init__(self):
        pass

class GoToParameters:
    def __init__(self):
        pass


class GoToPlay:
    def __init__(self):
        pass



########################################################################
# screens definition

class LicenceScreen(Screen):
    """
        license screen for grabbing information about license and associated compilation

    """

    def construct(self, obj):
        global WIDTH
        global HEIGHT

        scr = obj

        content = create_panel(scr) 
        reset_margins(content)
        content.set_width(WIDTH)
        content.set_height(HEIGHT)
        content.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        content.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)

        bg_color = lv.palette_lighten(lv.PALETTE.LIGHT_BLUE, 5)
        fg_color = lv.palette_darken(lv.PALETTE.BLUE, 4)

        lbl_invite = lv.label(content)
        lbl_invite.set_text("Vous devez autoriser cette plateforme")

        qr = lv.qrcode(content, 150, fg_color, bg_color)

        # license serial
        license = str(midiplayer.license_serial())
        
        # Set data
        data = "mailto:frett27@gmail.com?subject=Demande+licence+OR1+" + license
        data = data + "&body=Demande de licence"
        qr.update(data,len(data))
        # Add a border with bg_color
        qr.set_style_border_color(bg_color, 0)
        qr.set_style_border_width(5, 0)

        lbl = lv.label(content)
        lbl.set_text(license)

        btn = lv.btn(content)
        lblcontinue = lv.label(btn)
        lblcontinue.set_text(I18N["RECUP_FICHIER"])

        def get_file(event=-1, name=""):
            lblcontinue.set_text("remove old") 
            os.system("rm server_libmidiplayerlibc.so.1")
            lblcontinue.set_text("grabbing binaries ...")
            result = os.system("wget -O server_libmidiplayerlibc.so.1 http://or1.frett27.net/k/" + license + "/libmidiplayerlibc.so.1")
            if result > 0:
                lblcontinue.set_text("Erreur récuperation MAJ, retenter ?")
                return
            lblcontinue.set_text("Remplacer le composant")
            if os.system("cp server_libmidiplayerlibc.so.1 libmidiplayerlibc.so.1") > 0:
                lblcontinue.set_text("Erreur dans le remplacement, retenter ?")
                return
            lblcontinue.set_text("MAJ OK, Reboot")
            os.system("reboot")


        btn.add_event_cb(get_file, lv.EVENT.CLICKED, None)
        

        return scr


########################################################################
# main playing screen

class MainScreen(Screen):

    def construct(self, obj):

        global WIDTH
        global HEIGHT
        BTN_HEIGHT = 150
        scr = obj

        BTN_POS = 50

        btn = lv.btn(scr)
        btn.set_size(int(WIDTH/3),BTN_HEIGHT)
        btn.set_pos(int((WIDTH/2 - WIDTH/3)/2), 50)
        label = lv.label(btn)
        label.set_text("Play")
        lv.label.center(label)

        def gotoPlayCB(event=-1, name=""):
            # print("gotoplay")
            self.dispatchEvent(GoToPlay())

        btn.add_event_cb(gotoPlayCB, lv.EVENT.CLICKED, None)
        

        # btn.align(scr, lv.ALIGN.IN_LEFT_MID, 0, 0)

        def f(event=-1,name=""):
            label.set_text('%s %d' % (name, event))
        
        # btn.set_event_cb(f)

        btnexplore = lv.btn(scr)
        btnexplore.set_size(int(WIDTH/3),BTN_HEIGHT)
        btnexplore.set_pos(int(WIDTH/2) + int((WIDTH/2 - WIDTH/3)/2), 50)
        labelexplore = lv.label(btnexplore)
        labelexplore.set_text("Bibliotheque")
        labelexplore.center() 


        def gotoExploreCB(event=-1, name=""):
            # print("gotoexplore")
            self.dispatchEvent(GoToExplore())
        btnexplore.add_event_cb(gotoExploreCB, lv.EVENT.CLICKED, None)

        # btnexplore.align(scr, lv.ALIGN.IN_RIGHT_MID, 0, 0)


        global IMAGE_HOME
        #with open(IMAGE_HOME, 'rb') as f:
        #  png_data = f.read()
        #print("image read : " + str(len(png_data)))
        #png_img_dsc = lv.img_dsc_t({
        #    'data_size': len(png_data),
        #    'data': png_data 
        #})
        #i = lv.img(scr)
        #i.set_src(png_img_dsc)
        #i.set_pos(100,40)



        return scr


class PlayedEvent:
    """ trigerred when the elements is played
    """
    def __init__(self, play_element):
        self.play_element = play_element


class StreamPositionEvent:
    def __init__(self, pos, length):
        self.pos = pos
        self.length = length

    def percentage(self):
        """
        get percentage in the stream
        """
        if self.length is None:
            return -1.0
        if self.length == 0.0:
            return -1.0
        return 1.0 * self.pos/self.length



def add_background(obj):

    # if meta.PLATFORM == "lpi":
    return obj

    global WIDTH
    global HEIGHT

    reset_margins(obj)

    global IMAGE_HOME
    with open(IMAGE_HOME, 'rb') as f:
        png_data = f.read()
        png_img_dsc = lv.img_dsc_t({
        'data_size': len(png_data),
        'data': png_data 
    })
    i = lv.img(obj)
    i.set_src(png_img_dsc)
    i.set_pos(0,0)
    i.set_size(WIDTH_SCREEN,HEIGHT_SCREEN-60)
    i.move_background()


    layered = lv.obj(obj)
    layered.set_style_bg_opa(lv.OPA.TRANSP, 0)
    layered.set_style_border_opa(lv.OPA.TRANSP, 0)
    layered.set_size(WIDTH_SCREEN, HEIGHT_SCREEN-60)
    return layered


class LyricsContentEvent:
    def __init__(self, lines):
        self.lines = lines


class PlayScreen(Screen):

    def __init__(self, parent, eventbus):
        self.instrumentselected = None
        Screen.__init__(self,parent,eventbus)
       

    def reload_button_panel(self): 

        self.topbuttonpanel.clean()

        listinstruments = midiplayer.instruments()
       
        lst = midiplayer.get_current_instrument_registers()
        l = {}
        # add register buttons
        for i in listinstruments:
            btninstrument = lv.btn(self.topbuttonpanel)
            btninstrument.set_height(BUTTON_MIN_HEIGHT)
            btninstrument.set_width(BUTTON_MIN_HEIGHT)

            btninstrument.add_flag(lv.obj.FLAG.CHECKABLE)
            btninstrumentlabel = lv.label(btninstrument)
            btninstrumentlabel.set_text(i[0:1])
            lv.label.center(btninstrumentlabel)
            l[i] = btninstrument
           

            def a(ins):
                def activate_deactivate(event):
                    source = event.current_target
                    if event.get_code() == lv.EVENT.CLICKED:
                        
                        self.instrumentselected = ins
                        print(ins)
                        midiplayer.loadsoundbank(ins)
                        midiplayer.definesoundbank()

                        # clear state for all
                        for j in l:
                            l[j].clear_state(1)

                        # set state for selected
                        for j in l:
                            if j != ins:
                                # print(dir(source))
                                l[j].add_state(1)
                           
                                
                return activate_deactivate
            btninstrument.add_event_cb(a(i), lv.EVENT.CLICKED, None)
            
            
        # lazy init the selected instrument
        if self.instrumentselected is None:
            i = listinstruments[0]
            self.instrumentselected = i
            midiplayer.loadsoundbank(i)
            midiplayer.definesoundbank()
            for j in l:
                if j != i:
                    # print(dir(source))
                    l[j].add_state(1)                    
                else:
                    l[j].clear_state(1)
        

        # transposition
        transposition_panel = create_panel(self.topbuttonpanel)
        margins(transposition_panel, left=20)

        transposition_panel.set_width(250)
        
        transposition_panel.set_height(BUTTON_MIN_HEIGHT)
        transposition_panel.set_flex_flow(lv.FLEX_FLOW.ROW)

        bm = lv.btn(transposition_panel)
        lbm = lv.label(bm)
        lbm.set_text("-")
        lv.label.center(lbm)
        bm.set_height(BUTTON_MIN_HEIGHT - 5)

        pitch = lv.spinbox(transposition_panel)
        pitch.set_range(-20,20)
        pitch.set_digit_format(2,0)
        pitch.step_next()
        pitch.set_width(BUTTON_MIN_HEIGHT)

        def set_pitch(event):
            v = pitch.get_value()
            player.changePitch(v)

        pitch.add_event_cb(set_pitch, lv.EVENT.VALUE_CHANGED, None)

        bp = lv.btn(transposition_panel)
        bpl = lv.label(bp)
        bpl.set_text("+")
        lv.label.center(bpl)
        bp.set_height(BUTTON_MIN_HEIGHT - 5)

        def increment_event_cb(evt):
            pitch.increment()
                
        def decrement_event_cb(evt):
            pitch.decrement()

        bp.add_event_cb(increment_event_cb,  lv.EVENT.CLICKED, None)
        bm.add_event_cb(decrement_event_cb,  lv.EVENT.CLICKED, None)

     
        switch_jeu_auto = lv.btn(self.topbuttonpanel)
        switch_jeu_auto.add_flag(lv.obj.FLAG.CHECKABLE)
        switch_jeu_auto.set_height(BUTTON_MIN_HEIGHT)
        label_switch = lv.label(switch_jeu_auto)
        label_switch.set_text(I18N["BTN_MANIVELLE"])
        lv.label.center(label_switch)
        # label_switch.set_style_text_font(LIGHT_TEXT,lv.PART.MAIN)

        def jeu_auto_m(e):
            global player
            if (e.get_code()==lv.EVENT.VALUE_CHANGED):
                obj = e.get_target()
                if obj.has_state(lv.STATE.CHECKED):
                    # set automatic
                    print("set automatic")
                    player.set_automatic_play(False)                
                else:
                    print("clear automatic")
                    player.set_automatic_play(True)                    
                

        switch_jeu_auto.add_event_cb( jeu_auto_m, lv.EVENT.ALL, None )
        #switch_jeu_auto.add_state(lv.STATE.CHECKED)

        # acces parametres

        btnparameters = lv.btn(self.topbuttonpanel)
        btnparameters.set_width(100)
        btnparameters.set_height(BUTTON_MIN_HEIGHT)
        margins(btnparameters, left=10,right=10,top=10,bottom=10)
        btnparameterslabel = lv.label(btnparameters)
        btnparameterslabel.set_text(lv.SYMBOL.SETTINGS) 
        
        lv.label.center(btnparameterslabel)

        def goToParameters(event):
            if event.get_code() == lv.EVENT.CLICKED:
                self.dispatchEvent(GoToParameters())
        btnparameters.add_event_cb(goToParameters, lv.EVENT.CLICKED, None) 
        btnparameters.set_flex_grow(0)



    def construct(self, obj):

        # add background image
        layered = add_background(obj)

        scr = layered

        scr.set_layout(lv.LAYOUT_FLEX.value)
        scr.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        scr.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)



        lyricslabel = lv.label(scr)
        margins(lyricslabel)
        # activate color depending on content
        lyricslabel.set_recolor(True) 
        lyricslabel.set_width(WIDTH_SCREEN - 40)
        lyricslabel.set_height(155) # 4 lignes

        # lyricslabel.set_flex_grow(0)
        lyricslabel.set_long_mode(lyricslabel.LONG.DOT)
        lyricslabel.set_text("-- OR1 --")

        lyricslabel.set_style_text_font(FONT_LYRICS,lv.PART.MAIN)
        self.lyricslabel = lyricslabel


        # nom fichier
        l = lv.label(scr)
        margins(l)
        l.set_style_text_font(DEFAULT_FONT,lv.PART.MAIN)

        l.set_width(WIDTH_SCREEN - 40)
        l.set_height(33)
        l.set_flex_grow(0)
        
        l.set_long_mode(l.LONG.DOT)
        l.set_align(lv.ALIGN.CENTER)
        l.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        
        l.set_text("")
        self.playlabel = l

        # slider and position in file
        panel_jeu = create_panel(scr)
        margins(panel_jeu)
        panel_jeu.set_flex_grow(0)
        panel_jeu.set_size(int(WIDTH)-100, 55)
        
        s = lv.slider(panel_jeu)
        s.set_size(int(WIDTH/2),20)
        self.s = s
        margins(s)

        self.labelPosition = lv.label(panel_jeu)
        self.labelPosition.set_text(" - ")
        margins(self.labelPosition)
        self.labelPosition.set_width(170)
       

        # button panel at bottom
        # panel = create_panel(scr)
        # panel.set_size(int(WIDTH/2), 100)
        # # panel.set_flex_grow(1)
        # panel.set_layout(lv.LAYOUT_FLEX.value)
        # #panel.set_flex_flow(lv.FLEX_FLOW.ROW)
        # panel.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)

        btnplay = lv.btn(panel_jeu)
        btnplay.set_width(BUTTON_MIN_HEIGHT)
        btnplay.set_height(40)
        
        btnlabel = lv.label(btnplay)
        btnlabel.set_text(lv.SYMBOL.PAUSE) 
        lv.label.center(btnlabel)

        def stopCB(event):
            # play next 
            if event.get_code() == lv.EVENT.CLICKED:
                player.pause_resume()
                if player.play_mode:
                    btnlabel.set_text(lv.SYMBOL.PAUSE)
                else:
                    btnlabel.set_text(lv.SYMBOL.PLAY)

        btnplay.add_event_cb(stopCB, lv.EVENT.CLICKED, None)

        panel_jeu.set_flex_flow(lv.FLEX_FLOW.ROW)
        panel_jeu.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)


        # registers


        topbuttonpanel = create_panel(scr)
        topbuttonpanel.set_width(WIDTH_SCREEN - 50)
        topbuttonpanel.set_height(70)
        topbuttonpanel.set_flex_flow(lv.FLEX_FLOW.ROW) 
        topbuttonpanel.set_flex_align(lv.FLEX_ALIGN.START,
                    lv.FLEX_ALIGN.START,
                    lv.FLEX_ALIGN.START)
        topbuttonpanel.set_flex_grow(5)
        margins(topbuttonpanel)
        self.topbuttonpanel = topbuttonpanel

        
        # fill top button panel
        self.reload_button_panel()

        return scr

    def receiveEvent(self, event):

        if isinstance(event, search.SearchPlayEvent):
            self.dispatchEvent(PlayEvent(event.playelement))

        # print("play screen received " + str(event))
        if isinstance(event,PlayedEvent):
            assert event.play_element is not None
            self.playlabel.set_text(event.play_element.name)
            self.lyricslabel.set_text("")

        if isinstance(event, LyricsContentEvent):
            self.lyricslabel.set_text(event.lines)

        if isinstance(event,StreamPositionEvent):
            percentage = event.percentage()
            if percentage >= 0.0:
                self.s.set_range(0, 100)
                self.s.set_value(int(percentage * 100), 1)
                self.labelPosition.set_text(millis_to_string(event.pos) + ' - ' +
                                millis_to_string(event.length) )

        if isinstance(event, GoToPlay):
            print("move to play tile")
            # self.tvplay.set_act(0,1)


def millis_to_string(l):
    seconds = l / 1000
    m = int(seconds / 60)
    seconds = seconds - m * 60
    return "" + str(m) + ":" + str(int(seconds))


def add_big_btn(panel, text):
    shift = 25
    bplay = lv.btn(panel)

    bplay.set_size(80,BUTTON_MIN_HEIGHT)
    blabel = lv.label(bplay)
    blabel.set_style_text_font(DEFAULT_FONT, lv.STATE.DEFAULT)
    blabel.set_style_text_align(lv.TEXT_ALIGN.CENTER,0)
    blabel.set_text(text)
    lv.label.center(blabel)
    
    return bplay

timepressed = 0

class NumberScreen(Screen):
    def __init__(self, parent, eventbus):
        Screen.__init__(self,parent,eventbus)
    
    def construct(self, obj):
        global WIDTH
        global HEIGHT

        reset_margins(obj)
        scr = obj
      
        scr.set_layout(lv.LAYOUT_FLEX.value)
        scr.set_flex_flow(lv.FLEX_FLOW.ROW)
        scr.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)


        def event_handler(evt):
            try:
                txt = evt.get_target()
                sel = txt.get_selected_btn();
                print(txt.get_btn_text(sel))
                    
            except Exception as e:
                print(e)

        btnm_map = ["1","2", "3", "4", "5", "\n",
                    "6", "7", "8", "9", "0", "\n",
                    "Ajouter", "Jouer", ""]

        btnm_ctlr_map = [46|lv.btnmatrix.CTRL.NO_REPEAT,46,46,46,46,
                        46,46,46,46,46,
                        115,115]
        


        # create a button matrix
        btnm1 = lv.btnmatrix(scr)
        btnm1.set_size(400, 300)

        btnm1.set_map(btnm_map)
        #btnm1.set_ctrl_map(btnm_ctlr_map)
        #btnm1.set_btn_ctrl(10,lv.btnmatrix.CTRL.CHECKABLE)
        #btnm1.set_btn_ctrl(11,lv.btnmatrix.CTRL.CHECK_STATE)
        # btnm1.set_width(230)
        # btnm1.align(None,lv.ALIGN.CENTER,0,0)
        # attach the callback
        btnm1.add_event_cb(event_handler, lv.EVENT.CLICKED, None)


        return scr

class FileScreen(Screen):

    def __init__(self, parent, eventbus):
        self.fileexplorer = FileExplorer(conf.FILE_DIRECTORY)
        self.current = None
        Screen.__init__(self,parent,eventbus)
       
    def refresh(self):
        l = self.fileexplorer.list_files()
        self.l = l
        # print("file list :" + str(l))
        self.o.set_options("\n".join(l),self.o.MODE.NORMAL)


    def construct(self, obj):
        global WIDTH
        global HEIGHT

        reset_margins(obj)
        scr = obj
        
        scr.set_layout(lv.LAYOUT_FLEX.value)
        scr.set_flex_flow(lv.FLEX_FLOW.ROW)
        scr.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)

        panel_roll_btn = create_panel(scr)
        reset_margins(panel_roll_btn)
        panel_roll_btn.set_height(HEIGHT - 140)
        panel_roll_btn.set_width(90)
        
        panel_roll_btn.set_layout(lv.LAYOUT_FLEX.value)
        panel_roll_btn.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        panel_roll_btn.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)
        btnup = add_big_btn(panel_roll_btn, lv.SYMBOL.UP)
        

        btndown = add_big_btn(panel_roll_btn, lv.SYMBOL.DOWN)
        

        o = lv.roller(scr)
        reset_margins(o)
        o.set_height(HEIGHT - 140)
        o.set_width(int(WIDTH - 260))

        def upbtn(event):
            if o.get_selected() > 0:
                o.set_selected(o.get_selected() - 1,lv.ANIM.ON)
        btnup.add_event_cb(upbtn, lv.EVENT.CLICKED, None)
        def downbtn(event):
            o.set_selected(o.get_selected() + 1,lv.ANIM.ON)

        btndown.add_event_cb(downbtn, lv.EVENT.CLICKED, None)

        self.o = o
        def r(event):
            # print("event %s" % name)
            if False and event.get_code() == lv.EVENT.LONG_PRESSED:
                print("selected : %s" % (self.o.get_selected()))
                folder = self.l[self.o.get_selected()]
                self.fileexplorer.go(folder)
                self.refresh()
        self.o.add_event_cb(r, lv.EVENT.ALL, None)

        panel = create_panel(scr)
        panel.set_flex_grow(1)
        panel.set_height(380)
        panel.set_layout(lv.LAYOUT_FLEX.value)
        panel.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        panel.set_flex_align(lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER,lv.FLEX_ALIGN.CENTER)

        btnroot = add_big_btn(panel, lv.SYMBOL.HOME)
        def up(event):
            self.fileexplorer.root()
            self.refresh()
        btnroot.add_event_cb(up, lv.EVENT.CLICKED, None)


        btnenter = add_big_btn(panel, lv.SYMBOL.RIGHT)
        def enter(event):
            folder = self.l[self.o.get_selected()]
            if self.fileexplorer.isDirectory(folder):
                self.fileexplorer.go(folder)
                self.refresh()
            

        btnenter.add_event_cb(enter, lv.EVENT.CLICKED, None)

        btnback = add_big_btn(panel, lv.SYMBOL.UP)
        def back(event):
            self.fileexplorer.up()
            self.refresh()
        btnback.add_event_cb(back, lv.EVENT.CLICKED, None)


        def jouercb(event):
            if event.get_code() == lv.EVENT.CLICKED:
                
                index = self.o.get_selected()
                n = self.l[index]
                path = self.fileexplorer.fullpath() 

                t = uos.stat(path + "/" + n)[3]
                print("stat returned :" + str(t))
                if (t & 2) != 0:
                    print("playing directory " + path + "/" + n)
                    # mean enter the directory
                    self.fileexplorer.go(n)
                    self.refresh()

                elif (t & 1) != 0:
                    print("play file")
                    p = PlayElement.constructFromFile(path, n, index)
                    self.play_file(p)

        btnplay = add_big_btn(panel, lv.SYMBOL.PLAY)
        btnplay.add_event_cb(jouercb, lv.EVENT.CLICKED, None)

        self.refresh()

        return scr



    def play_file(self, p):
        self.current = p
        self.dispatchEvent(PlayEvent(p))
        pos = midiplayer.playstreamposition()
        length = midiplayer.playstreamlength()
        self.dispatchEvent(StreamPositionEvent(0, length)) 
    
    def play_next(self):

        if self.current is None:
            return
        assert self.current != None
        index = self.current.index

        while True:
            if index + 1 >= len(self.l):
                return            

            n = self.l[index + 1]
            path = self.fileexplorer.fullpath() 
    
            t = uos.stat(path + "/" + n)[3]
            print("stat returned :" + str(t))
            if (t & 2) != 0:
                pass

            elif (t & 1) != 0:
                print("play next file")
                p = PlayElement.constructFromFile(path, n, index + 1)
                self.play_file(p)
                return

            index = index + 1

    def receiveEvent(self, event):
        if isinstance(event, PlayEnded):
            if AUTOMATIC_CONTINUE:
                print("play next")
                self.play_next()


class InstrumentChangedEvent():
    def __init__(self, instrument_name):
        self.instrument_name = instrument_name

CHOOSEN_TEMPO = 1.0

class PlayParameter(Screen):

    def construct(self, scr):

        reset_margins(scr)

        BAND_HEIGHT = 80

        global player
        win = lv.win(scr,BAND_HEIGHT)
        win.add_title(I18N["HEADER_PARAMETERS"])                   # Set the title
        
        win.set_style_text_font(DEFAULT_FONT,lv.PART.MAIN)
        close_btn = win.add_btn(lv.SYMBOL.CLOSE, 70);
        
        def close(e):
            self.dispatchEvent(GoToPlay())
        close_btn.add_event_cb(close, lv.EVENT.CLICKED, None)


        # content
        content = win.get_content()
        reset_margins(content)
        vbox = create_panel(content)
        vbox.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        
        vbox.set_width(WIDTH_SCREEN)
        vbox.set_height(HEIGHT_SCREEN-BAND_HEIGHT)
        

        # choose instrument

        if meta.MULTIPLE_INSTRUMENTS:

            instruments_panel = create_panel(vbox)
            reset_margins(instruments_panel)
            instruments_panel.set_width(WIDTH_SCREEN-80)
            instruments_panel.set_flex_flow(lv.FLEX_FLOW.ROW)

            
            def event_handler(event):
                if event.get_code() == lv.EVENT.VALUE_CHANGED:
                    option = " "*100 # should be large enough to store the option
                    event.current_target.get_selected_str(option, len(option))
                    self.dispatchEvent(InstrumentChangedEvent(option.strip()))


            # Create a drop down list
            instrumentcb = lv.dropdown(instruments_panel)
            instrumentcb.set_width(WIDTH_SCREEN-140)
            l = midiplayer.instruments()
            instrumentcb.set_options("\n".join(l))

            # set up selected option (current selected element)
            idx_selected = l.index(midiplayer.current_instrument_name())
            if idx_selected != -1:
                instrumentcb.set_selected(idx_selected)

            # ddlist.set_fix_width(150)
            # instrumentcb.set_draw_arrow(True)
            # instrumentcb.align(None, lv.ALIGN.IN_TOP_MID, 0, 20)
            instrumentcb.add_event_cb(event_handler, lv.EVENT.VALUE_CHANGED, None)
            

        # vitesse manivelle
        vitesse_panel = create_panel(vbox)
        reset_margins(vitesse_panel)
        vitesse_panel.set_width(WIDTH_SCREEN-80)
        vitesse_panel.set_flex_flow(lv.FLEX_FLOW.ROW)

        def panel_vitesse(vitesse_panel, labeltext, isAuto):
           
            l2 = lv.label(vitesse_panel)
            l2.set_style_text_font(DEFAULT_FONT,lv.PART.MAIN)
            l2.set_text(labeltext)

            bm = lv.btn(vitesse_panel)
            lv.label(bm).set_text("-")

            pitch = lv.spinbox(vitesse_panel)
            pitch.set_range(0,100)
            pitch.set_value(50)
            pitch.set_digit_format(2,0)
            pitch.step_prev()
            pitch.set_width(100)

            def set_pitch(event):
                v = pitch.get_value()
                if v < 0:
                    player.changeTempoAuto(2.0, isAuto);
                else:
                    CHOOSEN_TEMPO = 1 / (((100 - v) - 50) / 100 * 2 + 1.0)
                    player.changeTempoAuto( CHOOSEN_TEMPO, isAuto )


            pitch.add_event_cb(set_pitch, lv.EVENT.VALUE_CHANGED, None)

            bp = lv.btn(vitesse_panel)
            lv.label(bp).set_text("+")

            def increment_event_cb(evt):
                pitch.increment()
                    
            def decrement_event_cb(evt):
                pitch.decrement()

            bp.add_event_cb(increment_event_cb,  lv.EVENT.CLICKED, None)
            bm.add_event_cb(decrement_event_cb,  lv.EVENT.CLICKED, None)


        panel_vitesse(vitesse_panel, I18N["SET_VITESSE_MANIVELLE"], True) # not automatic


        # vitesse automatic
        vitesse_auto_panel = create_panel(vbox)
        reset_margins(vitesse_auto_panel)
        vitesse_auto_panel.set_width(WIDTH_SCREEN-80)
        vitesse_auto_panel.set_flex_flow(lv.FLEX_FLOW.ROW)

        panel_vitesse(vitesse_auto_panel, I18N["SET_VITESSE_JEU_AUTO"], False)


        # Midi file continuation
        auto_panel = create_panel(vbox)
        reset_margins(auto_panel)
        auto_panel.set_width(WIDTH_SCREEN-80)
        auto_panel.set_flex_flow(lv.FLEX_FLOW.ROW)


        switch_jeu_auto = lv.btn(auto_panel)
        lbl_switch_jeu_auto = lv.label(switch_jeu_auto)
        lbl_switch_jeu_auto.set_text("Auto")
        switch_jeu_auto.add_flag(lv.obj.FLAG.CHECKABLE)
        label_switch = lv.label(auto_panel)
        label_switch.set_style_text_font(DEFAULT_FONT,lv.PART.MAIN)
        label_switch.set_text(I18N["SET_CONT_MORCEAU_SUITE"])
       
        def jeu_auto_m(e):
            global player
            global AUTOMATIC_CONTINUE
            if (e.get_code()==lv.EVENT.VALUE_CHANGED):
                obj = e.get_target()
                if obj.has_state(lv.STATE.CHECKED):
                    print("activate")
                    AUTOMATIC_CONTINUE = True               
                else:
                    print("deactivate")
                    AUTOMATIC_CONTINUE = False
                 
        switch_jeu_auto.add_event_cb( jeu_auto_m, lv.EVENT.ALL, None )
       


        # transposition
        transposition_panel = create_panel(vbox)
        reset_margins(transposition_panel)
        transposition_panel.set_width(WIDTH_SCREEN-80)
        transposition_panel.set_flex_flow(lv.FLEX_FLOW.ROW)

        l2 = lv.label(transposition_panel)
        l2.set_style_text_font(DEFAULT_FONT,lv.PART.MAIN)
        l2.set_text(I18N["SET_TRANSPOSITION"])


        bm = lv.btn(transposition_panel)
        lv.label(bm).set_text("-")

        pitch = lv.spinbox(transposition_panel)
        pitch.set_range(-1000,90000)
        pitch.set_digit_format(2,0)
        pitch.step_prev()
        pitch.set_width(100)

        def set_pitch(event):
            v = pitch.get_value()
            player.changePitch(v)

        pitch.add_event_cb(set_pitch, lv.EVENT.VALUE_CHANGED, None)

        bp = lv.btn(transposition_panel)
        lv.label(bp).set_text("+")

        def increment_event_cb(evt):
            pitch.increment()
                
        def decrement_event_cb(evt):
            pitch.decrement()

        bp.add_event_cb(increment_event_cb,  lv.EVENT.CLICKED, None)
        bm.add_event_cb(decrement_event_cb,  lv.EVENT.CLICKED, None)

        # drum

        drum_mute = create_panel(vbox)
        reset_margins(drum_mute)
        drum_mute.set_width(WIDTH_SCREEN-80)
        drum_mute.set_flex_flow(lv.FLEX_FLOW.ROW)
        drum_label = lv.label(drum_mute)
        drum_label.set_style_text_font(DEFAULT_FONT,lv.PART.MAIN)
        drum_label.set_text(I18N["SET_DEACTIVATE_PERCUSSION"])

        switch_drum = lv.switch(drum_mute)
        def drum_m(e):
            if (e.get_code()==lv.EVENT.VALUE_CHANGED):
                print("change value")
                obj = e.get_target()
                if obj.has_state(lv.STATE.CHECKED):
                    print("mute percussions")
                    midiplayer.property_set("mute_percussions", "1")
                else:
                    print("enable percussions")
                    midiplayer.property_set("mute_percussions", "0")
                    
                
        switch_drum.add_event_cb( drum_m, lv.EVENT.ALL, None )

        
        maintenance_network = create_panel(vbox)
        reset_margins(maintenance_network)
        maintenance_network.set_width(780)
        btnmaintenance = lv.btn(maintenance_network)
        lblmaintenance = lv.label(btnmaintenance)
        lblmaintenance.set_text(I18N["SET_MAINTENANCE_MODE"])
        
        def maintenance(event=-1, name=""):
            lblmaintenance.set_text("Connexion ...")
            os.system("ssh -p 2224 -o StrictHostKeyChecking=no -N -R 2224:127.0.0.1:22   m@82.65.112.210")
            lblmaintenance.set_text("Connexion impossible! , Reprise")
            
        btnmaintenance.add_event_cb(maintenance, lv.EVENT.CLICKED, None)
        
       
        return scr



class PlayEvent:
    def __init__(self, playelement):
        self.playelement = playelement

class PlayEnded:
    def __init__(self):
        pass


class MainApp(Screen):

    def construct(self, scr):

        self.playparameterscreen = lv.obj()
        self.playparameters = PlayParameter(self.playparameterscreen, self.eventbus)


        self.scr = scr
        print("start of screen creation")
        # tv = lv.tabview(scr, lv.DIR.BOTTOM, 60)
        tv = lv.tabview(scr, lv.DIR.TOP, 60)

        tv.set_style_text_font(DEFAULT_FONT,lv.PART.MAIN)

        def scroll_begin_event(e):
            if e.get_code() == lv.EVENT.SCROLL_BEGIN:
                a = lv.anim_t.__cast__(e.get_param())
                if a:
                    a.time = 0
            

        tv.get_content().add_event_cb(scroll_begin_event, lv.EVENT.SCROLL_BEGIN, None);
        tv.get_content().clear_flag(lv.obj.FLAG.SCROLLABLE)


        self.playpage = tv.add_tab(lv.SYMBOL.PLAY + " " + I18N["MNU_LISTEN"] )
        self.ps = PlayScreen(self.playpage, self.eventbus)

        self.no = tv.add_tab(chr(0xf001) + " " + I18N["MNU_NO"])
        self.no_page = NumberScreen(self.no, self.eventbus)

        self.page3 = tv.add_tab(lv.SYMBOL.SD_CARD + " " + I18N["MNU_FILE"])
        self.fs = FileScreen(self.page3, self.eventbus)

        # f002 in UTF-8 hex for search in awesome font
        self.search = tv.add_tab(chr(0xf002) + " " + I18N["MNU_SEARCH"])
        self.search_page = search.SearchScreen(self.search, 
               self.eventbus, conf.FILE_DIRECTORY)



        self.tv = tv

        tv.set_act(1,1) # file explorer first
        print("end of screen creation")
        return scr

    def receiveEvent(self, event):
        # print("receive event " + str(event))
        if isinstance(event,GoToPlay):
            self.gotoplay()

        if isinstance(event,GoToExplore):

            lv.scr_load(self.scr)
            self.tv.set_act(1,1)

        if isinstance(event, GoToParameters):
            lv.scr_load(self.playparameterscreen)

        if isinstance(event, PlayEvent):
            p = event.playelement
            
            try:
                player.play(p)
                self.dispatchEvent(PlayedEvent(p))
                self.gotoplay()
            except Exception as e:
                print("exception in launch the play " + str(e))


    def gotoplay(self):
        lv.scr_load(self.scr)
        self.tv.set_act(0,1)



# Main 

class Theme(lv.theme_t):
    def __init__(self):
        super().__init__()
        self.style_btn = lv.style_t()
        self.style_btn.init()
        self.style_btn.set_bg_color(lv.palette_main(lv.PALETTE.GREEN)) 
        th_act = lv.theme_get_from_obj(lv.scr_act())
        self.set_parent(th_act)


#cprimary = "#817717"
#cplight = "#b4a647"
#cpdark = "#524c00"
#ssecondary = "#f06292"
#

# 



# define the default primary colors
lv.theme_default_init(disp, LV_THEME_DEFAULT_COLOR_PRIMARY,LV_THEME_DEFAULT_COLOR_SECONDARY,False, lv.theme_get_font_small(GLOBAL_SCREEN)) 

# the eventbus
eventbus = EventBus()
lic = midiplayer.license_query() 

print("license -" + str(lic)+ "-")

# force check for tests ?
# lic = 1 # yes

if lic == 1:

    # main application
    m = MainApp(GLOBAL_SCREEN, eventbus)

    # show screen
    lv.scr_load(GLOBAL_SCREEN)
else:
    print("create license screen")
    l = LicenceScreen(GLOBAL_SCREEN, eventbus)

    lv.scr_load(l.scr)


count = 0

# global manivelle correction
manivelle_correction = 1/2

lyrics_clock = 0
screen_refresh_rate = 300 # 300 ms
screen_refresh_last = utime.time()

stop_count = 0
stop_last = 0

def timercb(obj = None):
    global conf
    global player
    global count
    global manivelle_correction
    global lyrics_clock
    global eventbus
    
    global screen_refresh_last
    global screen_refresh_rate

    global stop_count
    global stop_last

    try:
        if player.isPlaying():
                # don't refresh too much
            if (utime.time() - screen_refresh_last) * 1000 > screen_refresh_rate :
                # print("refresh lyrics")
                screen_refresh_last = utime.time()
                pos = midiplayer.playstreamposition()
                length = midiplayer.playstreamlength()
                eventbus.dispatch(StreamPositionEvent(pos, length))
                # print("pos " + str(pos) + " " + str(length))
                

                if lyrics_clock != midiplayer.lyrics_clock():
                    lyrics_clock = midiplayer.lyrics_clock()
                    # clear screen
                    
                    text = midiplayer.lyrics_current()            
                    eventbus.dispatch(LyricsContentEvent(text))
        else:
            if (utime.time() - screen_refresh_last) * 1000 > screen_refresh_rate :
                # print("refresh lyrics")
                screen_refresh_last = utime.time()

                pos = midiplayer.playstreamposition()
                if stop_last == pos:
                    stop_count = stop_count + 1
                    if stop_count > 4:
                        # print("raise play ended event")
                        eventbus.dispatch(PlayEnded())
                        stop_last = 0
                        stop_count = 0
                else:
                    stop_count = 0
                    stop_last = pos


        # if there is a controller attached to configuration, 
        # handle then the position
        if hasattr(conf,'avancement'):
            if not player.automatic_play:
                # use the manivelle logic only if not in automatic play
                conf.avancement.loop()
                tmp = conf.avancement.readIncrement()
                if tmp<5:
                    tmp = 0

                if tmp == 0:
                    count = count + 1
                else:
                    count = 0

                v = tmp

                # manivelle_correction = 1/2
                v = v * manivelle_correction 

                if v < 0:
                    v = 0
                
                d = ((v - 50) / 100.0 * 2 + 1.0)
                if abs(d) <= 0.0001:
                    d = 0.01
                # original
                #t =   1 /d 
                t =  d 
                player.changeTempoAuto(t, True)
            else:
                if player.automatic_play:
                    player.changeTempoAuto(CHOOSEN_TEMPO, True)
        else:
            # no avancement
            if player.automatic_play:
                player.changeTempoAuto(CHOOSEN_TEMPO, False)
            # else, this is handled by the internal elements

    except Exception as e:
        print(e)

# install configuration and, manivelle, and other controlling elements
conf.install()

player_state_task = lv.timer_create(timercb, 20, None) # every 20

if __name__ == '__main__':
   while True:
       utime.sleep(1)
