#-*- coding: utf-8 -*-
'''
Created on Dec 20, 2010

@author: zavlab1
'''
import gtk
from foobnix.util import LOG, const
from foobnix.helpers.my_widgets import tab_close_button, notetab_label
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.regui.model import FModel
from foobnix.regui.treeview.playlist_tree import PlaylistTreeControl
from foobnix.util.mouse_utils import is_double_left_click, is_double_middle_click,\
    is_middle_click, is_rigth_click
from foobnix.util.file_utils import get_file_path_from_dnd_dropped_uri
from foobnix.helpers.menu import Popup
import threading
from foobnix.util.key_utils import is_key

class TabGeneral(gtk.Notebook, FControl):
    def __init__(self, controls):
        gtk.Notebook.__init__(self)
        FControl.__init__(self, controls)
        self.controls = controls
        self.set_scrollable(True)
        
    def to_eventbox(self, widget):
        event = gtk.EventBox()
        event.add(widget)
        event.set_visible_window(False)
        event.show_all()
        return event
    
    def button(self, tab_child):
            if FC().tab_close_element == "button":
                return tab_close_button(func=self.on_delete_tab, arg=tab_child)
            elif FC().tab_close_element == "label":
                return notetab_label(func=self.on_delete_tab, arg=tab_child, angle=90)
            
    def on_delete_tab(self, tab_child):
        n = self.page_num(tab_child)    
        self.remove_page(n)
        
    def get_text_label_from_tab(self, tab_child, need_box_lenth = False):
        
            eventbox = self.get_tab_label(tab_child)
            box = eventbox.get_child()
            box_lenth = len(box.get_children())
            if type(box.get_children()[0]) == gtk.Label:
                label_object = box.get_children()[0]
            else: label_object = box.get_children()[1]
            text_of_label = label_object.get_label()
            if need_box_lenth:
                return text_of_label, box_lenth
            else: return text_of_label
       
            
    
    def on_rename_tab(self, tab_child, angle = 0):
        """get old label value"""
        n = self.page_num(tab_child)
        old_label_text, box_lenth = self.get_text_label_from_tab(tab_child, True)
        
        window = gtk.Window()
        window.set_decorated(False)
        window.set_position(gtk.WIN_POS_MOUSE)
        window.set_border_width(5)
        entry = gtk.Entry()
        entry.set_text(old_label_text)
        entry.show()
        
        def on_key_press(w, e):
            if is_key(e, 'Escape'):
                window.hide()
                entry.set_text(old_label_text)
            elif is_key(e, 'Return'):
                window.hide()
                new_label_text = entry.get_text()
                if new_label_text:
                    label = gtk.Label(new_label_text + ' ')
                    label.set_angle(angle)
                    if angle:
                        new_vbox = gtk.VBox()
                        if box_lenth > 1:
                            new_vbox.pack_start(self.button(tab_child.get_child()), False, False)
                        new_vbox.pack_end(label, False, False)
                    else:
                        new_vbox = gtk.HBox()
                        if box_lenth > 1:
                            new_vbox.pack_end(self.button(tab_child.get_child()), False, False)
                        new_vbox.pack_start(label, False, False)
                    event = gtk.EventBox()
                    event.add(new_vbox)
                    event = self.tab_menu_creator(event, tab_child)
                    event.set_visible_window(False)
                    event.connect("button-press-event", self.on_button_press)
                    event.show_all()
                    self.set_tab_label(tab_child, event)
                    FC().tab_names[n] = new_label_text
        
        def on_focus_out(*a):
            window.hide()
            entry.set_text(old_label_text)
            
        window.connect("key_press_event", on_key_press)
        window.connect("focus-out-event", on_focus_out)
        window.add(entry)
        window.show_all()

TARGET_TYPE_URI_LIST = 80
dnd_list = [ ('text/uri-list', 0, TARGET_TYPE_URI_LIST) ]

class NoteTabControl(TabGeneral, LoadSave):
    def __init__(self, controls):
        TabGeneral.__init__(self, controls)
        
        self.default_angle = 0
        self.last_notebook_page = ""
        self.active_tree = None
        self.set_show_border(True)
        self.stop_handling = False
        
        self.connect("button-press-event", self.on_button_press) 
        self.connect('drag-data-received', self.on_system_drag_data_received)
        
        self.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_DROP, dnd_list, gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_COPY) #@UndefinedVariable
        
        if not FC().cache_pl_tab_contents:
            self.empty_tab()
        
    def on_system_drag_data_received(self, widget, context, x, y, selection, target_type, timestamp):
        if target_type == TARGET_TYPE_URI_LIST:
            uri = selection.data.strip('\r\n\x00')
            uri_splitted = uri.split() # we may have more than one file dropped
            paths = []
            for uri in uri_splitted:
                path = get_file_path_from_dnd_dropped_uri(uri)
                paths.append(path)
            
            self.controls.check_for_media(paths)
                    
    def on_button_press(self, w, e, tab_content = None):
        """there were two problems in the handler:
        1. when you click on eventbox, appears extra the signal from the notebook
        2. when double-clicking, the first click is handled"""
        
        if type(w) == gtk.EventBox: 
            self.stop_handling = True
            #add delay in the background
            def start_handling():
                self.stop_handling = False
            threading.Timer(0.3, start_handling).start()
        
        #Get rid of the parasitic signal    
        if self.stop_handling and type(w) != gtk.EventBox: 
            return
        
        #handling of double middle click
        if is_double_middle_click(e) and type(w) == gtk.EventBox:
            #this variable helps to ignore first click, when double-clicking
            self.val = False
            self.on_rename_tab(tab_content)
                    
        #handling of middle click    
        elif is_middle_click(e):
            self.val = True
            
            def midclick():
                if self.val:
                    if type(w) == gtk.EventBox:
                        n = self.page_num(tab_content)
                        self.remove_page(n)
                    else:
                        self.empty_tab()
            #add delay in the background
            #for check (is second click or not)
            threading.Timer(0.5, midclick).start()
                        
        #to show context menu       
        elif is_rigth_click(e):
            if type(w) == gtk.EventBox:
                w.menu.show_all()
                w.menu.popup(None, None, None, e.button, e.time)    
 
               
    def tab_menu_creator(self, widget, tab_child):   
        widget.menu = Popup()
        widget.menu.add_item(_("Rename tab"), "", lambda: self.on_rename_tab(tab_child, self.default_angle), None)
        widget.menu.add_item(_("Close tab"), gtk.STOCK_CLOSE, lambda: self.on_delete_tab(tab_child), None)
        widget.show()
        return widget   
        
    def create_plus_tab(self):
        if self.get_n_pages() > 1:
            self.remove_page(self.page_num(self.plus_tab_child))
        append_label = notetab_label(func=self.empty_tab, arg=None, angle=0, symbol="+")
        self.plus_tab_child = notetab_label(func=self.empty_tab, arg=None, angle=0, symbol="Click me")
        self.prepend_page(self.plus_tab_child, append_label)
      
    def append_tab(self, name, beans=None):
        
        self.last_notebook_page = name
        LOG.info("append new tab")
        try:
            LOG.info("encoding of tab name is", name)
            name = unicode(name) #convert from any encoding in ascii
            LOG.info("encoding finished ", name)
        except:
            LOG.warn("problem of encoding definition for tab name is occured")
        
        if name and (FC().len_of_tab > -1) and (len(name) > FC().len_of_tab):
            name = name[:FC().len_of_tab]
        
        tab_content = self.create_notebook_tab(beans)
        
        def label():
            """label"""
            if name.endswith(" "):
                label = gtk.Label(name)
            else:
                label = gtk.Label(name + " ")
            label.show()
            label.set_angle(self.default_angle)
            #self.tab_labes.append(label)
            return label
                    
        """container Vertical Tab"""
        vbox = gtk.VBox(False, 0)
        vbox.show()
        if FC().tab_close_element:
            vbox.pack_start(self.button(tab_content), False, False, 0)
        vbox.pack_end(label(), False, False, 0)
        
        """container Horizontal Tab"""
        hbox = gtk.HBox(False, 0)
        hbox.show()
        if FC().tab_close_element:
            hbox.pack_end(self.button(tab_content), False, False, 0)
        hbox.pack_start(label(), False, False, 0)
         
        """container BOTH"""
        box = vbox if FC().tab_position == "left" else hbox
        event = self.to_eventbox(box)
        event = self.tab_menu_creator(event, tab_content)
        event.connect("button-press-event", self.on_button_press, tab_content)  
        event.show_all
        
        """append tab"""
        self.prepend_page(tab_content, event)
                
        self.set_tab_reorderable(tab_content, True)
        
        self.create_plus_tab()
                
        self.set_current_page(1)
                
        if self.get_n_pages() - 1 > FC().count_of_tabs:
            self.remove_page(self.get_n_pages() - 1)
        
    """def button(self, tab_content):
        if FC().tab_close_element == "button":
            return tab_close_button(func=self.on_delete_tab, arg=tab_content)
        else:
            return notetab_label(func=self.on_delete_tab, arg=tab_content, angle=self.default_angle)"""
    
    def set_tab_left(self):
        LOG.info("Set tabs Left")
        self.set_tab_pos(gtk.POS_LEFT)
        self.default_angle = 90
        self.set_show_tabs(True)
        FC().tab_position = "left"
        for page in xrange(self.get_n_pages()-1, 0, -1):
            print "cycle"
            print "page: ", page
            tab_content = self.get_nth_page(page)
            label_text = self.get_text_label_from_tab(tab_content)
            vbox = gtk.VBox()
            label = gtk.Label(label_text)
            label.set_angle(90)
            print label.get_angle()
            if FC().tab_close_element:
                vbox.pack_start(self.button(tab_content), False, False, 0)
            vbox.pack_end(label, False, False, 0)
            event = self.to_eventbox(vbox)
            event = self.tab_menu_creator(event, tab_content)
            event.connect("button-press-event", self.on_button_press, tab_content) 
            self.set_tab_label(tab_content, event)
        
    def set_tab_top(self):
        LOG.info("Set tabs top")
        self.set_tab_pos(gtk.POS_TOP)
        self.default_angle = 0
        self.set_show_tabs(True)
        FC().tab_position = "top"
        for page in xrange(self.get_n_pages()-1, 0, -1):
            print "page: ", page
            tab_content = self.get_nth_page(page)
            label_text = self.get_text_label_from_tab(tab_content)
            hbox = gtk.HBox()
            label = gtk.Label(label_text)
            label.set_angle(0)
            if FC().tab_close_element:
                hbox.pack_end(self.button(tab_content), False, False, 0)
            hbox.pack_start(label, False, False, 0)
            event = self.to_eventbox(hbox)
            event = self.tab_menu_creator(event, tab_content)
            event.connect("button-press-event", self.on_button_press, tab_content) 
            self.set_tab_label(tab_content, event)
        
    def set_tab_no(self):
        LOG.info("Set tabs no")
        self.set_show_tabs(False)
        
    def create_notebook_tab(self, beans):
        treeview = PlaylistTreeControl(self.controls)
        self.set_active_tree(treeview)
        treeview.append_all(beans)
        treeview.scroll.show_all()
        return  treeview.scroll
  
    def on_load(self):
        if FC().tab_position == "no": self.set_tab_no()
        elif FC().tab_position == "left": self.set_tab_left()
        else: self.set_tab_top()
        print "in on_load"
        print "FC().cache_pl_tab_contents: ",FC().cache_pl_tab_contents
        print len(FC().cache_pl_tab_contents)
        for page in xrange(0, len(FC().cache_pl_tab_contents)):
            if FC().cache_pl_tab_contents[page] == []:
                self.append_tab(FC().tab_pl_names[page], None, None)
                continue
            
            print  "FC().tab_pl_names: ", FC().tab_pl_names 
            
            self.controls.append_to_new_notebook(FC().tab_pl_names[page], FC().cache_pl_tab_contents[page])
   
    def on_save(self):
        number_music_tabs = self.get_n_pages()-1
        print "number_music_tabs: ", number_music_tabs
        FC().cache_pl_tab_contents = []
        FC().tab_pl_names = []
        if number_music_tabs > 0:
            for page in xrange(number_music_tabs, 0, -1):
                print "page: ", page
                tab_content = self.get_nth_page(page)
                pl_tree = tab_content.get_child()
                beans = pl_tree.get_all_beans()
                
                print "FC().cache_pl_tab_contents: befor", FC().cache_pl_tab_contents
                
                FC().cache_pl_tab_contents.append(beans)
                        
                FC().tab_pl_names.append(self.get_text_label_from_tab(self, tab_content))
    
    def empty_tab(self, *a):
        self.append_tab("Foobnix", [])
    
    def get_active_tree(self):
        return self.active_tree
    
    def append_all(self, beans):
        self.active_tree.append_all(beans)
    
    def next(self):
        bean = self.active_tree.next()
        return bean

    def prev(self):
        bean = self.active_tree.prev()
        return bean
    
    def set_active_tree(self, tree):
        self.active_tree = tree

    def set_playlist_tree(self):
        self.active_tree.set_playlist_tree()

    def set_playlist_plain(self):
        self.active_tree.set_playlist_plain()

    