class Button(object):
    def __init__(self, name, comp_id, colour=None, enabled=True):
        self.name = name
        self.comp_id = comp_id
        self.colour = colour
        self.enabled = enabled
        
    def to_html_element(self, url):
        id_base = "%s_%s" % (str(id(self)), self.comp_id)
        form_id = "form_%s" % id_base
        btn_id = "btn_%s" % id_base
        return """
            <form method="post" action="{url}" style="display:none" id="{form_id}"></form>            
            <button class="btn btn-mini" id="{button_id}">{btn_name}</button>            
            <script type="text/javascript">
                $("#{button_id}").click(function() {{
                     $("#{form_id}").submit();
                }});
            </script>
        """.format(url=url, form_id=form_id, button_id=btn_id, btn_name=self.name)
    
class TimeButton(Button):
    def __init__(self, name, comp_id, time, colour=None, enabled=True):
        super(TimeButton, self).__init__(name, comp_id, colour, enabled)
        self.time = time
        self.url_base = 'spend_time'
        self.url_kwargs = {'comp_id': self.comp_id, 'time': self.time}
        
class CompleteButton(Button):
    def __init__(self, comp_id, colour=None, enabled=True):
        super(CompleteButton, self).__init__("Complete", comp_id, colour, enabled)
        self.url_base = 'complete'
        self.url_kwargs = {'comp_id': self.comp_id}