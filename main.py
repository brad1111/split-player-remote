import gi
gi.require_version("Gtk","3.0")
gi.require_version("Playerctl","2.0")
from gi.repository import Gtk, Playerctl
from xdg import BaseDirectory
import os.path
from urllib import request, parse

# setup cache dir
cachedir = os.path.join(BaseDirectory.xdg_cache_home, "split-music-remote")


class Handler: 
    def __init__(self):
        print("hi")

    def on_windowPlayback_destroy(self, *args):
        Gtk.main_quit()

    def on_buttonPlayPause_clicked(self, button): 
        player.play_pause()

    def on_buttonNext_clicked(self, button):
        player.next()

    def on_buttonPrevious_clicked(self, button):
        player.previous()

    def on_buttonShuffleToggle_toggled(self, button):
        player.set_shuffle(not player.get_property("shuffle"))

    def on_buttonRepeatToggle_toggled(self, button):
        print("not implemented")
        button.set_active(False)

    def on_buttonPrevious_clicked(self, button):
        player.previous()

    def format_time(value):
        totalSeconds = value // 1000000
        minutes = int(totalSeconds // 60)
        seconds = int(totalSeconds % 60)
        return "{:n}:{:0>2}".format(minutes,seconds)

    def on_scaleSeek_format_value(self,scale,value):
        return Handler.format_time(value)

    def on_scaleVolume_format_value(self,scale,value):
        return "{:.0%}".format(value)

    def on_scaleSeek_change_value(self,scale,scrollType,position):
        player.set_position(position)

    def on_scaleVolume_change_value(self,scale,scrollType,volume):
        player.set_volume(volume)

builder = Gtk.Builder()
builder.add_from_file("ui.glade")
builder.connect_signals(Handler())

window = builder.get_object("windowPlayback")
window.show_all()

class PlayerHandler:
    def on_metadata_changed(player, metadata):
        labelTitle = builder.get_object("labelTitle")
        labelTitle.set_label(player.get_title()) 
        
        labelArtist = builder.get_object("labelArtist")
        labelArtist.set_label(player.get_artist())

        if 'mpris:artUrl' in metadata.keys():
            artUrl = metadata["mpris:artUrl"]
            
            #get filename and where to place it
            fileName = parse.urlparse(artUrl).path.split('/')[-1]
            imageLocation = os.path.join(cachedir, fileName)
            print(parse.urlparse(artUrl))
            if not os.path.isfile(imageLocation):
                request.urlretrieve(artUrl, imageLocation)

            imageThumbnail = builder.get_object("imageThumbnail")
            imageThumbnail.set_from_file(imageLocation)
        else:
            imageThumbnail = builder.get_object("imageThumbnail")
            imageThumbnail.set_from_icon_name("image-missing", 4)

        # set max song length
        if 'mpris:length' in metadata.keys():
            length = metadata["mpris:length"]
            adjustmentSeek = builder.get_object("adjustmentSeek")
            adjustmentSeek.set_upper(length)
            
            labelSongLength = builder.get_object("labelSongLength")
            labelSongLength.set_label(Handler.format_time(length))

#        PlayerHandler.update_volume()
#       
#    def update_volume():
#       scaleVolume = builder.get_object("scaleVolume")
#       volume = player.props.volume * 100
#       print(volume)
#       scaleVolume.set_value(volume)
    def on_volume_changed(player, volume):
        scaleVolume = builder.get_object("scaleVolume")
        scaleVolume.set_value(volume)

    def on_seek_changed(player, position):
        scaleSeek = builder.get_object("scaleSeek")
        scaleSeek.set_value(position)

player = Playerctl.Player()
player.connect("metadata", PlayerHandler.on_metadata_changed)
player.connect("volume", PlayerHandler.on_volume_changed)
player.connect("seeked", PlayerHandler.on_seek_changed)



Gtk.main()
