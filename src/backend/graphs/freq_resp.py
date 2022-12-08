


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure



class plotToolbar(NavigationToolbar):
    
    def __init__(self, canvas, parent):
        
        self.toolitems = (
            ('Home', 'Back to the main plot view', 'home', 'home'),
            ('Back', 'consectetuer adipiscing elit', 'back', 'back'),
            ('Forward', 'sed diam nonummy nibh euismod', 'forward', 'forward'),
            (None, None, None, None),
            ('Pan', 'tincidunt ut laoreet', 'move', 'pan'),
            ('Zoom', 'dolore magna aliquam', 'zoom_to_rect', 'zoom'),

            # new button in toolbar
            ("Customize", "Edit axis, curve and image parameters", "subplots", "edit_parameters"),                    

            (None, None, None, None),
            ('Subplots', 'putamus parum claram', 'subplots', 'configure_subplots'),
            ('Save', 'sollemnes in futurum', 'filesave', 'save_figure'),
            
        )
        super().__init__(canvas, parent)

    def edit_parameters(self):
        print("You have to create edit_parameters()")