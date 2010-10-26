#-*- coding: utf-8 -*-
'''
Created on Oct 3, 2010

@author: anton.komolov
'''
import gtk
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.regui.model import FModel
from foobnix.dm.dm_bean import DMBean
    
class DownloadManager(gtk.Window, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title(_("Download Manager"))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_geometry_hints(self, min_width=700, min_height=400)
        self.set_resizable(False)
        self.connect("delete-event", self.hide_window)
        self.connect("configure-event", self.on_configure_event)
        self.set_icon(self.controls.trayicon.get_pixbuf())

        self.beans = []
        self.stat = {'active': 0, 'complite': 0}

        vbox = gtk.VBox(False, 0)
        vbox.show()

        vbox.pack_start(self.line_add(), False, False, 0)
        vbox.pack_start(self.line_control(), False, False, 0)
        vbox.pack_start(self.line_list(), True, True, 0)

        self.add(vbox)

    def _add_button(self, text='Ok', stock=None, func=None, param=None):
        bt = gtk.Button(text)
        if stock:
            image = gtk.Image()
            image.set_from_stock(stock, gtk.ICON_SIZE_BUTTON)
            bt.set_image(image)
        if func:
            if param:
                bt.connect("clicked", lambda * a: func(param))
            else:
                bt.connect("clicked", lambda * a: func())
        bt.show()
        return bt


    def line_add(self):
        hbox = gtk.HBox(False, 0)
        hbox.show()

        self.entry = gtk.Entry()
        self.entry.show()
        #self.entry.set_text('http://.mp3')

        bt_add = self._add_button(_("Add"), gtk.STOCK_ADD, self.add_click)

        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_start(bt_add, False, False, 0)

        return hbox

    def line_control(self):
        hbox = gtk.HBox(True, 0)
        hbox.show()

        _buttons = [[_("Start All"), gtk.STOCK_MEDIA_PLAY, self.start_all],
                   [_("Stop All"), gtk.STOCK_MEDIA_STOP, self.stop_all],
                   [_("Clear list"), gtk.STOCK_OK, self.clear_all],
                   [_("Preferences"), gtk.STOCK_PREFERENCES, self.controls.show_preferences]]
        for b in _buttons:
            bt = self._add_button(*b)
            hbox.pack_start(bt, False, True, 0)

        return hbox

    def line_list(self):
        swin = gtk.ScrolledWindow()
        swin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        swin.show()

        vbox = gtk.VBox(False, 0)
        vbox.show()

        self.dm_list = vbox
        swin.add_with_viewport(vbox)

        return swin

    def _start_all(self):
        i = self.stat['active']
        if i < self.max_active_count:
            for dmbean in self.beans:
                if dmbean.is_ready() and dmbean.enable:
                    dmbean.start()
                    i += 1
                    if i >= self.max_active_count:
                        break

    def auto_start(self):
        if self.auto_start_donwload:
            self._start_all()

    def start_all(self):
        self.auto_start_donwload = True
        self._start_all()

    def stop_all(self):
        self.auto_start_donwload = False
        for dmbean in self.beans:
            dmbean.stop()

    def clear_all(self):
        beans = self.beans[:]
        for dmbean in beans:
            dmbean.clear()

    def add_click(self):
        bean_path = None
        bean_text = self.entry.get_text()
        if bean_text.lower().startswith('http://') and bean_text.lower().endswith('.mp3'):
            bean_path = bean_text
        bean = FModel(text = bean_text, path = bean_path)
        self.add_bean(bean)

    def _add_bean(self, bean):
        dmbean = DMBean(bean, self.save_path)
        dmbean.fill_bean_from_vk = self.controls.fill_bean_from_vk
        dmbean.on_clear = self.on_clear_dmbean
        dmbean.on_start = self.on_start_dmbean
        dmbean.on_stopped = self.on_stopped_dmbean
        dmbean.on_complite = self.on_complite_dmbean
        dmbean.show()
        self.beans.append(dmbean)
        self.dm_list.pack_start(dmbean, False, False, 0)

    def add_bean(self, bean):
        print 'Add_Bean'
        self._add_bean(bean)
        self.update_status()
        self.auto_start()

    def add_beans(self, beans):
        print 'Add_Beans'
        for bean in beans:
            self._add_bean(bean)
        self.update_status()
        self.auto_start()

    def on_clear_dmbean(self, dmbean, wait):
        if not wait:
            self.stat['complite'] -= 1
        self.beans.remove(dmbean)
        dmbean.hide()
        self.update_status()

    def on_start_dmbean(self, dmbean):
        self.stat['active'] += 1
        self.update_status()

    def on_stopped_dmbean(self, dmbean):
        self.stat['active'] -= 1
        self.update_status()
        self.auto_start()

    def on_complite_dmbean(self, dmbean):
        self.stat['active'] -= 1
        self.stat['complite'] += 1
        self.update_status()
        self.auto_start()

    def update_status(self):
        total = len(self.beans)
        active =  self.stat['active']
        complite = self.stat['complite']
        wait = total - active - complite
        if total:
            self.controls.statusbar.set_text(_('Downloads - Total: %s Active: %s Wait: %s Complite: %s') %
                                            (total, active, wait, complite))
        for dmbean in self.beans:
            dmbean.enable = active < self.max_active_count
            dmbean.update()

    def hide_window(self, *a):
        self.hide()
        return True

    def destroy(self):
        self.hide()
        return True

    def on_configure_event(self, w, e):
        pass

    def on_save(self, *a):
        self.stop_all()

    def on_load(self):
        self.save_path = FC().online_music_path
        self.max_active_count = FC().max_active_count
        self.auto_start_donwload = FC().auto_start_donwload