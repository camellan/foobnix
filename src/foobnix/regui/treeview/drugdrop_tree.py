'''
Created on Oct 14, 2010

@author: ivan
'''
import gtk
import copy
import uuid
import gobject
from foobnix.regui.model import FModel, FTreeModel
from foobnix.util import LOG
from foobnix.util.id3_util import update_id3_wind_filtering
from foobnix.util.iso_util import get_beans_from_iso_wv
from foobnix.util.m3u_utils import m3u_reader

VIEW_PLAIN = 0
VIEW_TREE = 1

class DrugDropTree(gtk.TreeView):
    def __init__(self, controls):
        self.controls = controls
        gtk.TreeView.__init__(self)
        
        self.connect("drag-drop", self.on_drag_drop)
        
        """init values"""
        self.hash = {None:None}
        self.current_view = None
    
    def configure_recive_drug(self):
        self.enable_model_drag_dest([("example1", 0, 0)], gtk.gdk.ACTION_COPY) #@UndefinedVariable
    
    def configure_send_drug(self):
        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example1", 0, 0)], gtk.gdk.ACTION_COPY) #@UndefinedVariable
    
    def append_all(self, beans):
        LOG.debug("begin apeend all")
        if self.current_view == VIEW_PLAIN:
            self.plain_append_all(beans)            
        else:
            self.tree_append_all(beans)
    
    def append(self, bean):
        if self.current_view == VIEW_PLAIN:
            self.plain_append_all([bean])
        else:
            self.tree_append(bean)
                
    def set_type_plain(self):
        self.current_view = VIEW_PLAIN
    
    def set_type_tree(self):
        self.current_view = VIEW_TREE
    
    def updates_tree_structure(self):
        for row in self.model:
            row[self.parent_level[0]] = None
            row[self.level[0]] = uuid.uuid4().hex             
            self.update_tree_structure_row_requrcive(row)
    
    def update_tree_structure_row_requrcive(self, row):        
        for child in row.iterchildren():
                child[self.parent_level[0]] = row[self.level[0]]
                child[self.level[0]] = uuid.uuid4().hex   
                self.update_tree_structure_row_requrcive(child)
   
    def get_bean_from_model_iter(self, model, iter):
        if not model or not iter:
            return None
        bean = FModel()
        id_dict = FTreeModel().cut().__dict__
        for key in id_dict.keys():
            num = id_dict[key]
            val = model.get_value(iter, num)
            setattr(bean, key, val)
        return bean
    
    def iter_copy(self, from_filter_model, from_filter_iter, to_filter_model, to_filter_iter, pos, to_type, from_type):
        
        
        
        #to_model = to_filter_model.get_model()
        #from_filter_path = from_filter_model.get_path(from_filter_iter) #only before changing in the tree
        
        if to_filter_iter:
            to_filter_path = to_filter_model.get_path(to_filter_iter)
            #to_filter_iter_has_child = to_filter_model.iter_has_child(to_filter_iter) #only before changing in the tree
                
        '''"""if m3u is dropped"""
        if (from_filter_model.get_value(from_filter_iter, 0).endswith(".m3u") 
        or from_filter_model.get_value(from_filter_iter, 0).endswith(".m3u8")):
            tree_store = from_filter_model.get_model()
            child_iter = from_filter_model.convert_iter_to_child_iter(from_filter_iter)
            m3u_file_path = tree_store.get_value(child_iter, 5)
            m3u_title = tree_store.get_value(child_iter, 0)
            self.controls.on_add_files(m3u_reader(m3u_file_path), m3u_title)'''
    
    
        if (to_type == VIEW_TREE and from_type == VIEW_TREE) and from_filter_model == to_filter_model:
            print "in if"
            
            if to_filter_iter and to_filter_iter_has_child: 
                print "to child"
                return new_iter
            
            try:
                if (from_filter_path[0] > to_filter_path[0] and 
                    pos != gtk.TREE_VIEW_DROP_INTO_OR_BEFORE and 
                    pos != gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
                    
                    from_filter_path = (from_filter_path[0] + 1, )
            except (TypeError, UnboundLocalError):
                pass
              
            from_filter_iter = from_filter_model.get_iter(from_filter_path)
            
            if from_filter_model.iter_has_child(from_filter_iter):
                for i in xrange(from_filter_model.iter_n_children(from_filter_iter)):
                    print "in cycle"
                    from_filter_iter = from_filter_model.get_iter(from_filter_path)
                    child_from_filter_iter = from_filter_model.iter_nth_child(from_filter_iter, i)
                    #path = from_filter_model.get_path(child_from_filter_iter)
                    row = self.get_row_from_model_iter(from_filter_model, child_from_filter_iter)
                    if pos == gtk.TREE_VIEW_DROP_BEFORE:
                        new_iter = new_iter_1
                    child_new_iter = to_model.insert_after(new_iter, None, row)
                    #print "@@@@@@@@",self.get_row_from_model_iter(from_filter_model, child_from_filter_iter)
                    #child_from_filter_iter = from_filter_model.get_iter(path)
                    #if from_filter_model.iter_has_child(child_from_filter_iter):
                        #print path
                        #self.iter_copy(from_filter_model, child_from_filter_iter, to_filter_model, child_new_iter, pos, to_type, from_type)
            return new_iter 
                
        if ((to_type == VIEW_TREE and from_type == VIEW_TREE) or
            (to_type == VIEW_PLAIN and from_type == VIEW_TREE)):            
            
            """3)tree to tree, tree to plain"""
            if from_filter_model.iter_has_child(from_filter_iter):
                print "has child"
                #cue_iters = []
                #folder_iters = []
                not_cue_iters = []
                
                """if there are cue-files in iters, display only them and subfolder"""  
                for i in range(0, from_filter_model.iter_n_children(from_filter_iter)):
                     
                    next_iter_to_copy = from_filter_model.iter_nth_child(from_filter_iter, i)
                    if (from_filter_model.get_value(next_iter_to_copy, 0).endswith(".m3u") 
                    or from_filter_model.get_value(next_iter_to_copy, 0).endswith(".m3u8")):
                        continue
                    elif from_filter_model.get_value(next_iter_to_copy, 0).endswith(".cue"):
                        cue_iters.append(next_iter_to_copy)
                    else:
                        if from_filter_model.iter_has_child(next_iter_to_copy):
                            folder_iters.append(next_iter_to_copy)
                        not_cue_iters.append(next_iter_to_copy)
                if cue_iters:
                    for next_iter_to_copy in cue_iters + folder_iters:
                        if from_filter_model.iter_has_child(next_iter_to_copy):
                            self.iter_copy(from_filter_model, next_iter_to_copy, to_filter_model, new_iter, pos, to_type, from_type)
                        row = self.get_row_from_model_iter(from_filter_model, next_iter_to_copy) 
                        new_iter = to_model.insert_after(None, new_iter, row)
                        
                else:
                    for next_iter_to_copy in not_cue_iters:
                        if from_filter_model.iter_has_child(next_iter_to_copy):
                            self.iter_copy(from_filter_model, next_iter_to_copy, to_filter_model, new_iter, pos, to_type, from_type)
                        row = self.get_row_from_model_iter(from_filter_model, next_iter_to_copy) 
                        new_iter = to_model.insert_after(None, new_iter, row)
                        
                        #self.iter_copy(from_filter_model, next_iter_to_copy, to_filter_model, new_iter, pos, to_type, from_type)
        else:
            """3)plain to tree, plain to plain"""
            print "in else"
            parent_level = row[self.level[0]]
            self.add_reqursive_plain(from_filter_model, from_filter_iter, to_filter_model, new_iter, parent_level)
                   
        return new_iter
    
    def add_reqursive_plain(self, from_model, from_iter, to_model, to_iter, parent_level):
        for child_row in self.get_child_rows(from_model, parent_level):            
            new_iter = to_model.get_model().append(to_iter, child_row)
            child_level = child_row[self.level[0]]
            self.add_reqursive_plain(from_model, from_iter, to_model, new_iter, child_level)
    
    def get_child_rows(self, model, parent_level):
        result = []
        for child_row in model:
            if child_row[self.parent_level[0]] == parent_level:
                result.append(child_row)        
        return result
    
    def on_drag_drop_finish(self):
        pass
    
    def on_drag_drop(self, to_tree, drag_context, x, y, selection):
        to_filter_model = to_tree.get_model()
        
        if to_tree.get_dest_row_at_pos(x, y):
            to_filter_path, to_filter_pos = to_tree.get_dest_row_at_pos(x, y)
            #to_path = to_filter_model.convert_path_to_child_path(to_path)      
            to_filter_iter = to_filter_model.get_iter(to_filter_path)
        else:
            to_filter_path = None
            to_filter_pos = None     
            to_filter_iter = None
        
        from_tree = drag_context.get_source_widget()        
        
        if not from_tree: return None
        
        from_filter_model, from_filter_paths = from_tree.get_selection().get_selected_rows()
        from_model = from_filter_model.get_model()
        to_model = to_filter_model.get_model()
        if to_filter_iter: 
            to_iter = to_filter_model.convert_iter_to_child_iter(to_filter_iter)
        else:
            to_iter = None
        new_iter = None
        for i, from_filter_path  in enumerate(from_filter_paths):
            from_filter_iter = from_filter_model.get_iter(from_filter_path)
            from_path = from_filter_model.convert_path_to_child_path(from_filter_path)
            from_iter = from_model.get_iter(from_path)
            #print from_path
            """do not copy to himself"""
            if to_tree == from_tree and from_filter_path == to_filter_path:
                drag_context.finish(False, False)
                return None
            
            """if m3u is dropped"""
            if (from_filter_model.get_value(from_filter_iter, 0).endswith(".m3u") 
            or from_filter_model.get_value(from_filter_iter, 0).endswith(".m3u8")):
                m3u_file_path = from_model.get_value(from_iter, 5)
                m3u_title = from_model.get_value(from_iter, 0)
                self.controls.on_add_files(m3u_reader(m3u_file_path), m3u_title)
            
            row = self.get_row_from_model_iter(from_filter_model, from_filter_iter)
            
            if from_model.iter_n_children(from_iter):
                new_iter = self.to_add_drug_item(to_model, to_iter, row, to_filter_pos)
                self.iter_is_parent(from_iter, from_model, to_model, new_iter)
            else:
                if new_iter:
                    to_iter = new_iter
                new_iter = self.to_add_drug_item(to_model, to_iter, row, to_filter_pos)
            
                        
            #"""do not copy to child""" 
            
            
            
            '''if new_iter: 
                to_filter_iter = to_filter_model.convert_child_iter_to_iter(new_iter)
                try:
                    if from_filter_path[0] > to_filter_path[0]:
                        from_filter_iter = from_filter_model.get_iter( (from_filter_path[0]+i, ) )
                except TypeError:
                    pass
            
            new_iter = self.to_add_drug_item(to_model, to_iter, row, to_filter_pos)'''
            
            if to_tree.current_view == VIEW_TREE:             
                self.updates_tree_structure()
                
            if to_tree.current_view == VIEW_PLAIN:             
                self.rebuild_as_plain()
        
        '''def task(i):
            if from_filter_model == to_filter_model:
                #n = i
                try:
                    if current_path[0]-i > to_filter_path[0]-i:
                        
                        to_filter_iter = to_filter_model.get_iter(to_filter_path)
                        
                        n = 0 if to_filter_model.iter_has_child(to_filter_iter) else 1
                        
                        while i > -1:
                            from_model.remove(from_model.get_iter( (from_path[0]+n,  ) ) )
                            i -= 1 
                    
                    elif current_path[0]-i < to_filter_path[0]-i:
                        from_filter_iter = from_filter_model.get_iter(current_path)
                        n = 0 if from_filter_model.iter_parent(from_filter_iter) else i
                        while i > -1:
                            from_model.remove(from_model.get_iter( (from_path[0]-n,  ) ) )
                            i -= 1
                
                except TypeError:
                    from_filter_iter = from_filter_model.get_iter(current_path)
                    n = 0 if from_filter_model.iter_parent(from_filter_iter) else i
                    while i > -1:
                            from_model.remove(from_model.get_iter( (from_path[0]-n,  ) ) )
                            i -= 1
            
            if to_tree.current_view == VIEW_TREE:             
                self.updates_tree_structure()
                
            if to_tree.current_view == VIEW_PLAIN:             
                self.rebuild_as_plain()    
                
           
        gobject.idle_add(task, i)'''
        self.on_drag_drop_finish()
    
    def to_add_drug_item(self, to_model, to_iter, row,  pos):    
        
        if to_iter:
            if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
                new_iter = to_model.prepend(to_iter, row)
                #if to_filter_iter and to_filter_iter_has_child:
                    #new_iter = to_model.iter_parent(new_iter)
            elif pos == gtk.TREE_VIEW_DROP_BEFORE:
                new_iter_1 = to_model.insert_before(None, to_iter, row)
                new_iter = to_model.iter_next(new_iter_1)
            elif pos == gtk.TREE_VIEW_DROP_AFTER:
                new_iter = to_model.insert_after(None, to_iter, row)
            else:
                new_iter = to_model.append(None, row)
        else:
            new_iter = to_model.append(None, row)
        
        return new_iter

    def iter_is_parent(self, from_iter, from_model, to_model, to_parent_iter, pos=gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
        iters = self.content_filter(from_iter, from_model) #to_parent_iter = self.to_add_drug_item(to_model, to_iter, row, to_filter_pos)
        for iter in iters:
            child_row = self.get_row_from_model_iter(from_model, iter)
            to_child_iter = to_model.append(to_parent_iter, child_row)
            if  from_model.iter_n_children(iter):
                self.iter_is_parent(iter, from_model, to_model, to_child_iter)
    
    def content_filter(self, from_iter, from_model):
        cue_iters = []
        folder_iters = []
        not_cue_iters = []
        for n in xrange(from_model.iter_n_children(from_iter)):
            from_child_iter = from_model.iter_nth_child(from_iter, n)
            if (from_model.get_value(from_child_iter, 0).endswith(".m3u") 
                or from_model.get_value(from_child_iter, 0).endswith(".m3u8")):
                    continue
            elif from_model.get_value(from_child_iter, 0).endswith(".cue"):
                cue_iters.append(from_child_iter)
            else:
                if from_model.iter_has_child(from_child_iter):
                    folder_iters.append(from_child_iter)
                not_cue_iters.append(from_child_iter)
        return cue_iters+folder_iters if cue_iters else not_cue_iters

    def child_by_recursion(self, row, plain):
        for child in row.iterchildren():
                plain.append(child)
                self.child_by_recursion(child, plain)
    
    def rebuild_as_tree(self, *a):
        self.current_view = VIEW_TREE        
        plain = []
        for row in self.model:
            plain.append(row)
            self.child_by_recursion(row, plain)
        
        copy_beans = []
        for row in plain:
            bean = self.get_bean_from_row(row)
            copy_beans.append(bean)
        
        self.clear()
        
        self.tree_append_all(copy_beans)
    
        self.expand_all()
    
    def rebuild_as_plain(self, *a):
        self.current_view = VIEW_PLAIN
        plain = []
        for row in self.model:
            plain.append(row)
            self.child_by_recursion(row, plain)
        
        copy_beans = []
        for row in plain:
            bean = self.get_bean_from_row(row)
            copy_beans.append(bean)
            
        self.clear()
        
        self.plain_append_all(copy_beans)
        
    def tree_append_all(self, beans):
        if not beans:
            return None
        self.current_view = VIEW_TREE
        LOG.debug("append all as tree")
       
        for bean in beans:    
            self.tree_append(bean)
    
    def plain_append_all(self, beans):
        LOG.debug("begin plain append all")
        if not beans:
            return
        self.current_view = VIEW_PLAIN
        
        normilized = []
        for model in beans:
            if model.path and model.path.lower().endswith(".iso.wv"):
                LOG.debug("begin normalize iso.wv", model.path)
                all = get_beans_from_iso_wv(model.path)
                for inner in all:
                    normilized.append(inner)
            else:
                normilized.append(model)
        beans = normilized
              
        counter = 0
        for bean in beans:
            if bean.path and not bean.path.lower().endswith(".cue"):                                        
                if bean.is_file:
                    counter += 1
                    bean.tracknumber = counter
                else: 
                    counter = 0
            self._plain_append(bean)
            
    def _plain_append(self, bean):
        def task():
            LOG.debug("Plain append begin", bean.text, bean.path)
            
            LOG.debug("Plain append task", bean.text, bean.path)
            if not bean:
                return
            if bean.is_file == True:
                bean.font = "normal"
            else:
                bean.font = "bold"
                
            bean.visible = True
        
            beans = update_id3_wind_filtering([bean])
            for one in beans:
                one.update_uuid() 
                row = self.get_row_from_bean(one)            
                """append to tree thread safe"""
                
                self.model.append(None, row)            
                """append to tree thread safe end"""
        gobject.idle_add(task)
            
        
        
    def tree_append(self, bean):
        def task(bean):
            if not bean:
                return
            if bean.is_file == True:
                bean.font = "normal"
            else:
                bean.font = "bold"
            
            """copy beans"""
            bean = copy.copy(bean)
            bean.visible = True
        
            if self.hash.has_key(bean.get_parent()):
                parent_iter_exists = self.hash[bean.get_parent()]
            else:
                parent_iter_exists = None
            row = self.get_row_from_bean(bean)
            
            parent_iter = self.model.append(parent_iter_exists, row)
            self.hash[bean.level] = parent_iter
        
        gobject.idle_add(task, bean)
        
        
            
        
