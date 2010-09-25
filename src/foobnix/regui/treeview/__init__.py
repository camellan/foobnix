import gtk
import gobject
from deluge.log import LOG

class FModel():
    def __init__(self, none=False):        
        self.text = 0
        self.visible = 1
        self.font = 2
        self.play_icon = 3
        self.time = 4
        self.path = 5
        
        if none:
            self._none()
    
    def _none(self):
        for i in self.__dict__:
            self.__dict__[i] = None

class TreeViewControl(gtk.TreeView, FModel):
    
    def __init__(self):
        gtk.TreeView.__init__(self)   
        FModel.__init__(self)
             
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.set_enable_tree_lines(True)
        
        """model config"""
        self.model = gtk.TreeStore(str, gobject.TYPE_BOOLEAN, str, str, str)
        
        """filter config"""
        filter = self.model.filter_new()
        filter.set_visible_column(self.visible)
        self.set_model(filter)    
        
        """connectors"""
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-release-event", self.on_key_release)
        
    def append(self, level=None, text=None, visible=True, font="normal", play_icon=None, time=None):        
        return self.model.append(level, [text, visible, font, play_icon, time])
   
    def clear(self):
        self.model.clear()
        
    def  on_button_press(self, w, e):
        pass
    
    def  on_key_release(self, w, e):
        pass
    
    def get_selected_bean(self):
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        
        return self._get_bean_by_path(paths[0])
    
    def _get_bean_by_path(self, path):
        model = self.model
        iter = model.get_iter(path)
        if iter:
            bean = FModel(True)
            bean.text = model.get_value(iter, self.text)            
            return bean
        return None
    
    def get_all_selected_beans(self):
        selection = self.widget.get_selection()
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        beans = []
        for path in paths:       
            selection.select_path(path)     
            bean = self._get_bean_by_path(path)
            beans.append(bean)
        return beans
    
    def filter(self, query):
        LOG.info("Filter", query)
        if not query:
            """show alll"""
            for line in self.model:                
                line[self.visible] = True
                for child in line.iterchildren():
                    child[self.visible] = True
            self.collapse_all()
            return True

        """filter selected"""        
        query = query.lower()       
        for line in self.model:
            name = line[self.text].lower()

            if name.find(query) >= 0:
                LOG.info("FILTER FIND PARENT:", name, query)
                line[self.visible] = True
                self.expand_all()                    
            else:
                line[self.visible] = False
