from gi.repository import Gtk, Gdk


class TestWindow(Gtk.Window):

    def __init__(self):
        super().__init__(title="test")
        #super().__init__(1)

        # composite setup
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        self.set_visual(visual)
 
        self.connect("key_press_event", self.on_key_press)
        self.set_app_paintable(True)
        self.set_decorated(False)

    def on_key_press(self, widget, eventkey):
        print("----- key press -----")
        keyval = eventkey.get_keyval()[1]  # very ugly here
        print(keyval)
