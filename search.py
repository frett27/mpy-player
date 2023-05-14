
import meta

from app import *

import uos

class SearchAbort:
    pass

class SearchPlayEvent:
    def __init__(self, playelement):
        self.playelement = playelement

# screen for searching in a file collection
class SearchScreen(Screen):
    def __init__(self, parent, eventbus, root_folder):
        Screen.__init__(self,parent,eventbus)
        self.root_folder = root_folder

    def construct(self, scr):

        global WIDTH
        global HEIGHT
        
        def ta_event_cb(e,kb):
            code = e.get_code()
            ta = e.get_target()
            if code == lv.EVENT.FOCUSED:
                self.activate_kb()
            elif code == lv.EVENT.DEFOCUSED:
                self.unactivate_kb()

            # print("event " + str(code))
                
       
        # Create a text area. The keyboard will write here
        ta = lv.textarea(scr)
        ta.set_style_text_font(lv.font_montserrat_30, lv.PART.MAIN)
        
        ta.set_width(WIDTH - 60)
        ta.set_height(60)
        ta.align(lv.ALIGN.TOP_LEFT, 10, 10)
        ta.add_event_cb(lambda e: ta_event_cb(e,kb), lv.EVENT.ALL, None)
        ta.set_placeholder_text("Titre")
        self.ta = ta


        result_panel = create_panel(scr)
        self.result_panel = result_panel
        
        result_panel.set_size(WIDTH - 60, 300)
        
        #result_panel.set_layout(lv.LAYOUT_FLEX.value)
        result_panel.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        #result_panel.set_flex_grow(1)

        result_panel.align(lv.ALIGN.TOP_LEFT, 0, 80)
        reset_margins(result_panel)


        # Create a keyboard to use it with one of the text areas
        kb = lv.keyboard(scr)
        # kb.set_mode(lv.keyboard.MODE.NUMBER)

        kb.set_textarea(ta)

        def kb_events_cb(e):
            if (e.get_code() == lv.EVENT.READY):
                self.find()

            if (e.get_code() == lv.EVENT.CANCEL):
                self.dispatchEvent(SearchAbort())
            # print("keayboard event " + str(e.get_code()))
        
        kb.add_event_cb(kb_events_cb, lv.EVENT.ALL, None)
        self.kb = kb

        return scr

    def unactivate_kb(self):
        self.kb.set_textarea(None)
        self.kb.add_flag(lv.obj.FLAG.HIDDEN)

    def activate_kb(self):
        self.kb.set_textarea(self.ta)
        self.kb.clear_flag(lv.obj.FLAG.HIDDEN)


    def find(self):

        max_e = 40

        searchtext = self.ta.get_text()
        # validate a text
        print("search for : " + searchtext)
        l = []
        fp = []
        self.search_for(searchtext, self.root_folder, l, fp, max_e = max_e)
        # print("keyboard ready")
        # l.sort()
        print("result :" + str(l))

        ## remove all children
        self.result_panel.clean()

        for e in l:
            c = create_panel(self.result_panel)
            reset_margins(c)
            c.set_style_pad_left(10, lv.PART.MAIN)
            c.set_layout(lv.LAYOUT_FLEX.value)
            c.set_flex_flow(lv.FLEX_FLOW.ROW)
            c.set_width(WIDTH - 50)
            c.set_height(65)
            # c.set_flex_grow(1)

            i = l.index(e)

            element = PlayElement.constructFromFile(fp[i], e, i)

            def handle(element):
                def playbtn(e):
                    print("play " + str(element))
                    self.dispatchEvent(SearchPlayEvent(element))
                return playbtn

            btn = lv.btn(c)
            btn.add_event_cb(handle(element), lv.EVENT.CLICKED, None)

            lblbtn = lv.label(btn)
            lblbtn.set_text(lv.SYMBOL.PLAY)
            
            lbl = lv.label(c)
            lbl.set_long_mode(lv.label.LONG.DOT)            
            
            lbl.set_text(element.name)

        print("" + str(len(l)))
        if len(l) >= max_e:
            c = create_panel(self.result_panel)
            reset_margins(c)
            c.set_style_pad_left(10, lv.PART.MAIN)
            c.set_layout(lv.LAYOUT_FLEX.value)
            c.set_flex_flow(lv.FLEX_FLOW.ROW)
            c.set_width(WIDTH - 50)
            c.set_height(65)
            
            more = lv.label(c)
            more.set_text("...... trop de résultats affichables")


        if len(l) > 0:
            self.unactivate_kb()

    # search files, within the limit
    def search_for(self, search, folder , l, fullpath, max_e=30):
        print("enter " + folder)
        if len(l) >= max_e:
            return

        for entry in uos.ilistdir(folder):
            (name,t,inode) = entry
            # print(name)
            if name != "." and name != "..":
                subfolder = folder + "/" + name
                #m = uos.stat(subfolder)[3]
                if (t & 0x4000 ) != 0:
                    # directory
                    self.search_for(search, subfolder, l, fullpath, max_e)
                elif t & 0x8000 != 0:
                    lo = name.lower()
                    if lo.find(search) != -1:
                        l.append(name)
                        fullpath.append(folder)
                        if len(l) >= max_e:
                            return    

                else: 
                    print("ignore " + name + " " + str(m))

        # sort the element
        # l.sort()

    

import utime

if __name__ == "__main__":
    # test procedure


    # create screen
    scr = lv.obj()

    # by default, set the font to 22
    scr.set_style_text_font(lv.font_montserrat_22, lv.STATE.DEFAULT)

    # the eventbus
    eventbus = EventBus()

    # main application
    m = SearchScreen(scr, eventbus, meta.FILE_DIRECTORY)

    # show screen
    lv.scr_load(scr)


    # install configuration and, manivelle, and other controlling elements
    conf.install()

    while True:
        utime.sleep(1)



