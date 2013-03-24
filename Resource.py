from GUIElements import CompleteButton, TimeButton
from Utils import time_string

TIME_BUTTONS = [["+1m", 1], ["+5m", 5], ["+10m", 10], ["+15m", 15], ["+20m", 20], ["+30m", 30], ["+1h", 60]]  

class Resource(object):
    def __init__(self, db_row, component_rows):
        self.res_id = db_row['res_id'] 
        self.name = db_row['name']
        self.components = []
        
        for c_row in component_rows:
            self.add_component(Component(c_row))
        
    # Unnecessary?
    def to_db_data(self):
        return (self.res_id, self.name)
        
    def get_component(self, component_name):
        for component in self.components:
            if component.name == component_name:
                return component
        return None

    def add_component(self, component):        
        self.components.append(component)
        
    def complete_component(self, completed_component_name):
        for component in self.components:
            if component.name == completed_component_name:
                component.completed()
                return  
        
    def spend_time(self, time_spent, component_name):
        component = self.get_component(component_name)
        if component:
            component.spend_time(time_spent)
    
    def total_time(self):
        total_time = 0
        for component in self.components:
            total_time += component.time
        return total_time
    
    def total_time_string(self):
        return time_string(self.total_time())

    def __str__(self):
        string = self.name
        for component in self.components:
            string += "\n  %s" % component
        return string
        
        
class Component(object):
    def __init__(self, db_row):
        self.res_id = db_row['res_id']
        self.comp_id = db_row['comp_id'] 
        self.name = db_row['name']
        self.time = db_row['time']
        self.complete = db_row['complete']
        
    # Unnecessary?
    def to_db_data(self):
        return (self.res_id, self.name, self.time, self.complete)
    
    def spend_time(self, time_spent):
        self.time += time_spent
        
    def completed(self):
        self.complete = True
    
    def button_groups(self):
        b_grps = []
        if self.complete:
            return b_grps
        
        # Time buttons
        t_btn_grp = []
        for t_btn in TIME_BUTTONS:
            t_btn_grp.append(TimeButton(t_btn[0], self.comp_id, t_btn[1]))
        b_grps.append(t_btn_grp)
        
        # 'Done' button
        b_grps.append([CompleteButton(self.comp_id)])
        
        return b_grps
    
    def time_string(self):
        return time_string(self.time)
        
    def __str__(self):
        complete_string = "X" if self.complete else "O"
        return complete_string + " - " + self.name