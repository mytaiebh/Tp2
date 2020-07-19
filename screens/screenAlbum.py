#from screenAlbum.EditColorImageAdvanced import EditColorImageAdvanced
#from screenAlbum.EditConvertImage import EditConvertImage
#from screenAlbum.EditConvertVideo import EditConvertVideo
#from screenAlbum.EditCropImage import EditCropImage
#from screenAlbum.EditDenoiseImage import EditDenoiseImage
# from screenAlbum.EditFilterImage import EditFilterImage
# from screenAlbum.EditMain import EditMain
# from screenAlbum.EditNone import EditNone
# from screenAlbum.EditRotateImage import EditRotateImage
# from screenAlbum.PhotoViewer import PhotoViewer
# from screenAlbum.RemoveFromTagButton import RemoveFromTagButton
# from screenAlbum.RemoveTagButton import RemoveTagButton
# from screenAlbum.TagSelectButton import TagSelectButton
# from screenAlbum.VideoViewer import VideoViewer
# from screenAlbum.editBorderImage import EditBorderImage
# from screenAlbum.editColorImage import EditColorImage
from screenAlbum.factorySecrenAlbum import FactoryScreenAlbum
from screens.mpegAudioCommand import MpegAudioCommand
from screens.mpegCommand import MpegCommand


try:
    import numpy
    import cv2
    opencv = True
except:
    opencv = False
import sys
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os
import datetime
from shutil import copy2
import subprocess
import time
from models.PhotosTags import Tag, Photo

#all these are needed to get ffpyplayer working on linux

from ffpyplayer.player import MediaPlayer
from ffpyplayer import tools as fftools
import threading
from kivy.config import Config
Config.window_icon = "data/icon.png"
from kivy.app import App
from kivy.clock import Clock
from kivy.cache import Cache
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.core.image.img_pil import ImageLoaderPIL
from kivy.loader import Loader

from generalcommands import agnostic_path, local_path, time_index, format_size, to_bool, isfile2
from generalElements.labels.NormalLabel import NormalLabel
from generalElements.labels.ShortLabel import ShortLabel
from generalElements.popups.ScanningPopup import ScanningPopup
from generalElements.popups.NormalPopup import NormalPopup
from generalElements.popups.ConfirmPopup import ConfirmPopup
from generalElements.dropDowns.AlbumSortDropDown import AlbumSortDropDown
from generalconstants import *
from screenAlbum.treeViewInfo import TreeViewInfo
from kivy.lang.builder import Builder
Builder.load_string("""
<ScreenAlbum>:
    canvas.before:
        Color:
            rgba: app.theme.background
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'vertical'
        MainHeader:
            NormalButton:
                text: 'Back To Library'
                on_release: app.show_database()
            HeaderLabel:
                text: root.folder_title
            InfoLabel:
            DatabaseLabel:
            SettingsButton:
        BoxLayout:
            orientation: 'horizontal'
            SplitterPanelLeft:
                id: leftpanel
                #width: app.leftpanel_width
                BoxLayout:
                    orientation: 'vertical'
                    size_hint_x: .25
                    Header:
                        size_hint_y: None
                        height: app.button_scale
                        ShortLabel:
                            text: 'Sort:'
                        MenuStarterButtonWide:
                            id: sortButton
                            text: root.sort_method
                            on_release: root.sort_dropdown.open(self)
                        ReverseToggle:
                            id: sortReverseButton
                            state: root.sort_reverse_button
                            on_release: root.resort_reverse(self.state)
                    PhotoListRecycleView:
                        size_hint: 1, 1
                        id: albumContainer
                        viewclass: 'PhotoRecycleViewButton'
                        scroll_distance: 10
                        scroll_timeout: 200
                        bar_width: int(app.button_scale * .5)
                        bar_color: app.theme.scroller_selected
                        bar_inactive_color: app.theme.scroller
                        scroll_type: ['bars', 'content']
                        SelectableRecycleBoxLayout:
                            id: album
                            default_size: self.width, (app.button_scale * 2)
                    BoxLayout:
                        size_hint_y: None
                        disabled: app.simple_interface
                        opacity: 0 if app.simple_interface else 1
                        height: 0 if app.simple_interface else app.button_scale
                        orientation: 'horizontal'
                        WideButton:
                            text: 'Previous'
                            on_press: root.previous_photo()
                        WideButton:
                            text: 'Next'
                            on_press: root.next_photo()

            MainArea:
                size_hint_x: .5
                orientation: 'vertical'
                RelativeLayout:
                    id: photoViewerContainer
                Header:
                    height: app.button_scale if root.edit_panel == 'main' else 0
                    disabled: False if root.edit_panel == 'main' else True
                    opacity: 1 if root.edit_panel == 'main' else 0
                    id: buttonsFooter
                    NormalButton:
                        size_hint_y: 1
                        text: 'Full Screen'
                        on_press: root.fullscreen()
                    Label:
                        text: ''
                    NormalButton:
                        size_hint_y: 1
                        text: '1 month'
                        on_press: root.fullscreen()
                    Label:
                        text: ''   
                    NormalToggle:
                        size_hint_y: 1
                        text: '  Favorite  '
                        id: favoriteButton
                        state: 'down' if root.favorite else 'normal'
                        on_press: root.set_favorite()
                        disabled: app.database_scanning
                    NormalButton:
                        size_hint_y: 1
                        width: self.texture_size[0] + 20 if root.canprint else 0
                        opacity: 1 if root.canprint else 0
                        disabled: not root.canprint
                        id: printButton
                        text: '  Print  '
                        on_release: app.print_photo()
                    NormalButton:
                        size_hint_y: 1
                        id: deleteButton
                        warn: True
                        text: '  Delete  '
                        on_release: root.delete_selected_confirm()
                        disabled: app.database_scanning
            SplitterPanelRight:
                id: rightpanel
                width: 0
                opacity: 0
                PanelTabs:
                    tab: root.view_panel
                    BoxLayout:
                        tab: 'info'
                        opacity: 0
                        orientation: 'vertical'
                        pos: self.parent.pos
                        size: self.parent.size
                        padding: app.padding
                        Scroller:
                            NormalTreeView:
                                id: panelInfo
                        WideButton:
                            text: 'Refresh Photo Info'
                            on_release: root.full_photo_refresh()
                    BoxLayout:
                        tab: 'edit'
                        opacity: 0
                        id: editPanelContainer
                        pos: self.parent.pos
                        size: self.parent.size
                        padding: app.padding
                        ScrollerContainer:
                            cols: 1
                            id: editScroller
                            do_scroll_x: False
                            EditPanelContainer:
                                disabled: app.database_scanning
                                id: panelEdit
                                cols: 1
                                size_hint: 1, None
                                height: self.minimum_height
                    BoxLayout:
                        tab: 'tags'
                        opacity: 0
                        pos: self.parent.pos
                        size: self.parent.size
                        padding: app.padding
                        Scroller:
                            size_hint: 1, 1
                            do_scroll_x: False
                            GridLayout:
                                disabled: app.database_scanning
                                size_hint: 1, None
                                cols: 1
                                height: self.minimum_height
                                GridLayout:
                                    canvas.before:
                                        Color:
                                            rgba: app.theme.area_background
                                        BorderImage:
                                            pos: self.pos
                                            size: self.size
                                            source: 'data/buttonflat.png'
                                    padding: app.padding
                                    id: displayTags
                                    cols: 1
                                    size_hint: 1, None
                                    height: self.minimum_height
                                    NormalLabel:
                                        id: albumLabel
                                        text:"Current Tags:"
                                    GridLayout:
                                        id: panelDisplayTags
                                        size_hint: 1, None
                                        cols: 2
                                        height: self.minimum_height
                                MediumBufferY:
                                GridLayout:
                                    canvas.before:
                                        Color:
                                            rgba: app.theme.area_background
                                        BorderImage:
                                            pos: self.pos
                                            size: self.size
                                            source: 'data/buttonflat.png'
                                    padding: app.padding
                                    id: addToTags
                                    cols: 1
                                    size_hint: 1, None
                                    height: self.minimum_height
                                    NormalLabel:
                                        id: albumLabel
                                        text:"Add Tags:"
                                    GridLayout:
                                        id: panelTags
                                        size_hint: 1, None
                                        cols: 2
                                        height: self.minimum_height
                                MediumBufferY:
                                BoxLayout:
                                    canvas.before:
                                        Color:
                                            rgba: app.theme.area_background
                                        BorderImage:
                                            pos: self.pos
                                            size: self.size
                                            source: 'data/buttonflat.png'
                                    padding: app.padding
                                    orientation: 'vertical'
                                    size_hint: 1, None
                                    height: app.button_scale * 2 + app.padding * 2
                                    NormalLabel:
                                        text: "Create Tags:"
                                    BoxLayout:
                                        orientation: 'horizontal'
                                        size_hint: 1, None
                                        height: app.button_scale
                                        NormalInput:
                                            id: newTag
                                            multiline: False
                                            hint_text: 'Tag Name'
                                            input_filter: app.remove_unallowed_characters
                                        NormalInput:
                                            id: newPerson
                                            multiline: False
                                            hint_text: 'Person Name'
                                            input_filter: app.remove_unallowed_characters
                                        NormalButton:
                                            disabled: not root.can_add_tag(newTag.text)
                                            text: 'New'
                                            on_release: root.add_tag()
                                            size_hint_y: None
                                            height: app.button_scale
            StackLayout:
                size_hint_x: None
                width: app.button_scale
                VerticalButton:
                    state: 'down' if root.view_panel == 'info' else 'normal'
                    vertical_text: "Photo Info"
                    on_press: root.show_info_panel()
                VerticalButton:
                    state: 'down' if root.view_panel == 'edit' else 'normal'
                    vertical_text: "Editing"
                    on_press: root.show_edit_panel()
                VerticalButton:
                    state: 'down' if root.view_panel == 'tags' else 'normal'
                    vertical_text: "Tags"
                    on_press: root.show_tags_panel()

""")





class ScreenAlbum(Screen):
    makeScreenAlbum = FactoryScreenAlbum()
    """Screen layout of the album viewer."""
    view_panel = StringProperty('')
    sort_reverse_button = StringProperty('normal')
    opencv = BooleanProperty()
    folder_title = StringProperty('Album Viewer')
    canprint = BooleanProperty(True)
    ffmpeg = BooleanProperty(False)

    #Video reencode settings
    encoding = BooleanProperty(False)
    total_frames = NumericProperty()
    current_frame = NumericProperty()
    cancel_encoding = BooleanProperty()
    encoding_settings = {}
    encodingthread = ObjectProperty()
    encoding_process_thread = ObjectProperty()

    #Widget holder variables
    sort_dropdown = ObjectProperty()  #Holder for the sort method dropdown menu
    popup = None  #Holder for the screen's popup dialog
    edit_panel = StringProperty('')  #The type of edit panel currently loaded
    edit_panel_object = ObjectProperty(allownone=True)  #Holder for the edit panel widget
    viewer = ObjectProperty()  #Holder for the photo viewer widget
    imagecache = None  #Holder for the image cacher thread

    #Variables relating to the photo list view on the left
    selected = StringProperty('')  #The current folder/album/tag being displayed
    type = StringProperty('None')  #'Folder', 'Album', 'Tag'
    target = StringProperty()  #The identifier of the album/folder/tag that is being viewed
    photos = []  #Photoinfo of all photos in the album


    sort_method = StringProperty('Name')  #Current album sort method
    sort_reverse = BooleanProperty(False)

    # yvan not sure!
    app = App.get_running_app()
    app.config.set('Sorting', 'album_sort', sort_method)
    app.config.set('Sorting', 'album_sort_reverse', sort_reverse)


    #Variables relating to the photo view
    photoinfo = []  #photoinfo for the currently viewed photo
    photo = StringProperty('')  #The absolute path to the currently visible photo
    fullpath = StringProperty()  #The screenDatabase-relative path of the current visible photo
    orientation = NumericProperty(1)  #EXIF Orientation of the currently viewed photo
    angle = NumericProperty(0)  #Corrective angle rotation of the currently viewed photo
    mirror = BooleanProperty(False)  #Corrective mirroring of the currently viewed photo
    favorite = BooleanProperty(False)  #True if the currently viewed photo is favorited
    view_image = BooleanProperty(True)  #True if the currently viewed photo is an image, false if it is a video
    image_x = NumericProperty(0)  #Set when the image is loaded, used for orientation of cropping
    image_y = NumericProperty(0)  #Set when the image is loaded, used for orientation of cropping

    #Stored variables for editing
    edit_color = BooleanProperty(False)
    equalize = NumericProperty(0)
    autocontrast = BooleanProperty(False)
    adaptive = NumericProperty(0)
    brightness = NumericProperty(0)
    gamma = NumericProperty(0)
    shadow = NumericProperty(0)
    contrast = NumericProperty(0)
    saturation = NumericProperty(0)
    temperature = NumericProperty(0)
    edit_advanced = BooleanProperty(False)
    tint = ListProperty([1.0, 1.0, 1.0, 1.0])
    curve = ListProperty([[0, 0], [1, 1]])
    edit_filter = BooleanProperty(False)
    sharpen = NumericProperty(0)
    median = NumericProperty(0)
    bilateral = NumericProperty(0.5)
    bilateral_amount = NumericProperty(0)
    vignette_amount = NumericProperty(0)
    vignette_size = NumericProperty(0.5)
    edge_blur_amount = NumericProperty(0)
    edge_blur_size = NumericProperty(0.5)
    edge_blur_intensity = NumericProperty(0.5)
    edit_border = BooleanProperty(False)
    border_selected = StringProperty()
    border_x_scale = NumericProperty(0)
    border_y_scale = NumericProperty(0)
    border_opacity = NumericProperty(1)
    border_tint = ListProperty([1.0, 1.0, 1.0, 1.0])
    edit_denoise = BooleanProperty(False)
    luminance_denoise = StringProperty('10')
    color_denoise = StringProperty('10')
    search_window = StringProperty('15')
    block_size = StringProperty('5')
    edit_crop = BooleanProperty(False)
    crop_top = NumericProperty(0)
    crop_right = NumericProperty(0)
    crop_bottom = NumericProperty(0)
    crop_left = NumericProperty(0)

    def show_panel(self, panel_name):
        right_panel = self.ids['rightpanel']
        if self.view_panel == panel_name:
            self.set_edit_panel('main')
            right_panel.hidden = True
            self.view_panel = ''
            self.show_left_panel()
        else:
            self.set_edit_panel('main')
            self.view_panel = panel_name
            right_panel.hidden = False
            app = App.get_running_app()
            if app.simple_interface:
                self.hide_left_panel()

    def show_tags_panel(self, *_):
        self.show_panel('tags')

    def show_info_panel(self, *_):
        self.show_panel('info')

    def show_edit_panel(self, *_):
        self.show_panel('edit')

    def show_left_panel(self, *_):
        left_panel = self.ids['leftpanel']
        left_panel.hidden = False

    def hide_left_panel(self, *_):
        left_panel = self.ids['leftpanel']
        left_panel.hidden = True

    def cancel_encode(self, *_):
        """Signal to cancel the encodig process."""

        self.encoding = False
        self.cancel_encoding = True
        if self.encoding_process_thread:
            self.encoding_process_thread.kill()
        app = App.get_running_app()
        app.message("Canceled encoding.")

    def begin_encode(self):
        """Begins the encoding process, asks the user for confirmation with a popup."""

        self.set_edit_panel('main')
        self.encode_answer(self, 'yes')

    def encode_answer(self, instance, answer):
        """Continues the encoding process.
        If the answer was 'yes' will begin reencoding by starting the process thread.

        Arguments:
            instance: The widget that called this command.
            answer: String, 'yes' if confirm, anything else on deny.
        """

        del instance
        self.dismiss_popup()
        if answer == 'yes':
            app = App.get_running_app()
            self.viewer.stop()

            # Create popup to show progress
            self.cancel_encoding = False
            self.popup = ScanningPopup(title='Converting Video', auto_dismiss=False, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
            self.popup.scanning_text = ''
            self.popup.open()
            encoding_button = self.popup.ids['scanningButton']
            encoding_button.bind(on_press=self.cancel_encode)

            # Start encoding thread
            self.encodingthread = threading.Thread(target=self.encode_process)
            self.encodingthread.start()

    '''def get_ffmpeg_audio_command(self, video_input_folder, video_input_filename, audio_input_folder, audio_input_filename, output_file_folder, encoding_settings=None, start=None):
        if not encoding_settings:
            encoding_settings = self.encoding_settings
        if encoding_settings['file_format'].lower() == 'auto':
            audio_codec = 'aac'
            audio_bitrate = '192'
            extension = 'mp4'
        else:
            file_format = containers[containers_friendly.index(encoding_settings['file_format'])]
            audio_codec = audio_codecs[audio_codecs_friendly.index(encoding_settings['audio_codec'])]
            audio_bitrate = encoding_settings['audio_bitrate']
            extension = containers_extensions[containers.index(file_format)]

        if start is not None:
            seek = ' -ss '+str(start)
        else:
            seek = ''
        video_file = video_input_folder+os.path.sep+video_input_filename
        audio_file = audio_input_folder+os.path.sep+audio_input_filename
        output_filename = os.path.splitext(video_input_filename)[0]+'-mux.'+extension
        output_file = output_file_folder+os.path.sep+output_filename
        audio_bitrate_settings = "-b:a " + audio_bitrate + "k"
        audio_codec_settings = "-c:a " + audio_codec + " -strict -2"

        command = 'ffmpeg -i "'+video_file+'"'+seek+' -i "'+audio_file+'" -map 0:v -map 1:a -codec copy '+audio_codec_settings+' '+audio_bitrate_settings+' -shortest "'+output_file+'"'
        return [True, command, output_filename]'''


    def encode_process(self):
        """Uses ffmpeg command line to reencode the current video file to a new format."""

        app = App.get_running_app()
        self.encoding = True
        input_file = self.photo

        input_video = MediaPlayer(input_file, ff_opts={'paused': True, 'ss': 1.0, 'an': True})
        frame = None
        while not frame:
            frame, value = input_video.get_frame(force_refresh=True)
        input_metadata = input_video.get_metadata()
        input_video.close_player()
        input_video = None

        start_time = time.time()
        start_point = self.viewer.start_point
        end_point = self.viewer.end_point
        framerate = input_metadata['frame_rate']
        duration = input_metadata['duration']
        self.total_frames = (duration * (end_point - start_point)) * (framerate[0] / framerate[1])
        start_seconds = start_point * duration
        duration_seconds = (end_point * duration) - start_seconds

        pixel_format = input_metadata['src_pix_fmt']
        input_size = input_metadata['src_vid_size']
        input_file_folder, input_filename = os.path.split(input_file)
        output_file_folder = input_file_folder+os.path.sep+'reencode'
        #changment
        mpegCommand = MpegCommand()
        mpegCommand.set_input_folder(input_file_folder)
        mpegCommand.set_input_filename(input_filename)
        mpegCommand.set_output_file_folder(output_file_folder)
        mpegCommand.set_input_size(input_size)
        mpegCommand.set_input_framerate(framerate)
        mpegCommand.set_input_pixel_format(pixel_format)
        mpegCommand.set_start(start_seconds)
        mpegCommand.set_duration(duration_seconds)

        command_valid, command, output_filename = mpegCommand.ffmpeg_command()
        if not command_valid:
            self.cancel_encode()
            self.dismiss_popup()
            app.popup_message(text="Invalid FFMPEG command: " + command, title='Warning')
        print(command)

        output_file = output_file_folder+os.path.sep+output_filename
        if not os.path.isdir(output_file_folder):
            try:
                os.makedirs(output_file_folder)
            except:
                self.cancel_encode()
                self.dismiss_popup()
                app.popup_message(text='Could not create folder for encode.', title='Warning')
                return
        if os.path.isfile(output_file):
            try:
                os.remove(output_file)
            except:
                self.cancel_encode()
                self.dismiss_popup()
                app.popup_message(text='Could not create new encode, file already exists.', title='Warning')
                return

        #used to have 'shell=True' in arguments, is it still needed?
        self.encoding_process_thread = subprocess.Popen(command, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

        # Poll process for new output until finished
        progress = []
        while True:
            if self.cancel_encoding:
                self.encoding_process_thread.kill()
                if os.path.isfile(output_file):
                    self.delete_output(output_file)
                if not os.listdir(output_file_folder):
                    os.rmdir(output_file_folder)
                self.dismiss_popup()
                return
            nextline = self.encoding_process_thread.stdout.readline()
            if nextline == '' and self.encoding_process_thread.poll() is not None:
                break
            if nextline.startswith('frame= '):
                self.current_frame = int(nextline.split('frame=')[1].split('fps=')[0].strip())
                scanning_percentage = self.current_frame / self.total_frames * 100
                self.popup.scanning_percentage = scanning_percentage
                #time_done = nextline.split('time=')[1].split('bitrate=')[0].strip()
                elapsed_time = time.time() - start_time
                time_done = time_index(elapsed_time)
                remaining_frames = self.total_frames - self.current_frame
                try:
                    fps = float(nextline.split('fps=')[1].split('q=')[0].strip())
                    seconds_left = remaining_frames / fps
                    time_remaining = time_index(seconds_left)
                    time_text = "  Time: "+time_done+"  Remaining: "+time_remaining
                except:
                    time_text = ""
                self.popup.scanning_text = str(str(int(scanning_percentage)))+"%"+time_text
                progress.append(self.current_frame)
            sys.stdout.write(nextline)
            sys.stdout.flush()

        output = self.encoding_process_thread.communicate()[0]
        exit_code = self.encoding_process_thread.returncode

        error_code = ''
        if exit_code == 0:
            #encoding completed
            self.dismiss_popup()
            good_file = True

            if os.path.isfile(output_file):
                output_video = MediaPlayer(output_file, ff_opts={'paused': True, 'ss': 1.0, 'an': True})
                frame = None
                while not frame:
                    frame, value = output_video.get_frame(force_refresh=True)
                output_metadata = output_video.get_metadata()
                output_video.close_player()
                output_video = None
                if output_metadata:
                    if self.encoding_settings['width'] and self.encoding_settings['height']:
                        new_size = (int(self.encoding_settings['width']), int(self.encoding_settings['height']))
                        if output_metadata['src_vid_size'] != new_size:
                            error_code = ', Output size is incorrect'
                            good_file = False
                else:
                    error_code = ', Unable to find output file metadata'
                    good_file = False
            else:
                error_code = ', Output file not found'
                good_file = False

            if not good_file:
                Clock.schedule_once(lambda x: app.message('Warning: Encoded file may be bad'+error_code))

            new_original_file = input_file_folder+os.path.sep+'.originals'+os.path.sep+input_filename
            if not os.path.isdir(input_file_folder+os.path.sep+'.originals'):
                os.makedirs(input_file_folder+os.path.sep+'.originals')
            new_encoded_file = input_file_folder+os.path.sep+output_filename
            if not os.path.isfile(new_original_file) and os.path.isfile(output_file):
                try:
                    os.rename(input_file, new_original_file)
                    os.rename(output_file, new_encoded_file)
                    if not os.listdir(output_file_folder):
                        os.rmdir(output_file_folder)

                    #update screenDatabase
                    extension = os.path.splitext(output_file)[1]
                    new_photoinfo = list(self.photoinfo)
                    new_photoinfo[0] = os.path.splitext(self.photoinfo[0])[0]+extension  #fix extension
                    new_photoinfo[7] = int(os.path.getmtime(new_encoded_file))  #update modified date
                    new_photoinfo[9] = 1  #set edited
                    new_photoinfo[10] = new_original_file  #set original file
                    if self.photoinfo[0] != new_photoinfo[0]:
                        app.Photo.rename(self.photoinfo[0], new_photoinfo[0], new_photoinfo[1])
                    app.Photo.update(new_photoinfo)

                    # reload video in ui
                    self.fullpath = local_path(new_photoinfo[0])
                    newpath = os.path.join(local_path(new_photoinfo[2]), local_path(new_photoinfo[0]))
                    Clock.schedule_once(lambda x: self.set_photo(newpath))

                except:
                    app.popup_message(text='Could not replace original file', title='Warning')
                    return
            else:
                app.popup_message(text='Target file name already exists! Encoded file left in "/reencode" subfolder', title='Warning')
                return
            Clock.schedule_once(lambda x: app.message("Completed encoding file '"+self.photo+"'"))
        else:
            self.dismiss_popup()
            if os.path.isfile(output_file):
                self.delete_output(output_file)
            if not os.listdir(output_file_folder):
                os.rmdir(output_file_folder)
            app.popup_message(text='File not encoded, FFMPEG gave exit code '+str(exit_code), title='Warning')

        self.encoding = False

        #switch active video in photo list back to image
        self.show_selected()

    def set_photo(self, photo):
        self.photo = photo
        Clock.schedule_once(lambda *dt: self.refresh_all())

    def delete_output(self, output_file, timeout=20):
        """Continuously try to delete a file until its done."""

        start_time = time.time()
        while os.path.isfile(output_file):
            try:
                os.remove(output_file)
            except:
                time.sleep(0.25)
            if timeout != 0:
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    return False
        return True

    def on_sort_reverse(self, *_):
        """Updates the sort reverse button's state variable, since kivy doesnt just use True/False for button states."""

        app = App.get_running_app()
        self.sort_reverse_button = 'down' if to_bool(app.config.get('Sorting', 'album_sort_reverse')) else 'normal'

    def delete_original(self):
        """Tries to delete the original version of an edited photo."""

        app = App.get_running_app()
        deleted, message = app.delete_photo_original(self.photoinfo)
        if deleted:
            self.set_edit_panel('main')
        app.message(message)

    def delete_original_all(self):
        folder = self.photoinfo[1]
        app = App.get_running_app()
        deleted_photos = app.delete_folder_original(folder)
        if len(deleted_photos) > 0:
            app.message('Deleted '+str(len(deleted_photos))+' original files')
        else:
            app.message('Could not delete any original files')

    def restore_original(self):
        """Tries to restore the original version of an edited photo."""

        self.viewer.stop()
        app = App.get_running_app()
        edited_file = self.photo
        original_file = local_path(self.photoinfo[10])
        original_filename = os.path.split(original_file)[1]
        edited_filename = os.path.split(edited_file)[1]
        new_original_file = os.path.join(os.path.split(edited_file)[0], original_filename)
        if os.path.isfile(original_file):
            if os.path.isfile(edited_file):
                try:
                    os.remove(edited_file)
                except:
                    pass
            if os.path.isfile(edited_file):
                app.popup_message(text='Could not restore original file', title='Warning')
                return
            try:
                os.rename(original_file, new_original_file)
            except:
                pass
            if os.path.isfile(original_file) or not os.path.isfile(new_original_file):
                app.popup_message(text='Could not restore original file', title='Warning')
                return

            #update photo info
            if original_filename != edited_filename:
                edited_fullpath = os.path.split(self.photoinfo[0])[0]+'/'+original_filename
                app.Photo.rename(self.photoinfo[0], edited_fullpath, self.photoinfo[1])
                self.photoinfo[0] = edited_fullpath

            self.photoinfo[10] = os.path.basename(new_original_file)
            orientation = 1
            try:
                exif_tag = Image.open(edited_file)._getexif()
                if 274 in exif_tag:
                    orientation = exif_tag[274]
            except:
                pass

            self.photoinfo[13] = orientation
            self.photoinfo[9] = 0
            self.photoinfo[7] = int(os.path.getmtime(new_original_file))
            app.Photo.update(self.photoinfo)
            app.save_photoinfo(target=self.photoinfo[1],
                               save_location=os.path.join(self.photoinfo[2], self.photoinfo[1]))

            #regenerate thumbnail
            app.Photo.thumbnail_update(self.photoinfo[0], self.photoinfo[2], self.photoinfo[7], self.photoinfo[13],
                                          force=True)

            #reload photo image in ui
            self.fullpath = self.photoinfo[0]
            self.refresh_all()
            self.photo = new_original_file
            self.on_photo()
            self.clear_cache()
            app.message("Restored original file.")
            self.set_edit_panel('main')

            #switch active photo in photo list back to image
            self.show_selected()
        else:
            app.popup_message(text='Could not find original file', title='Warning')

    def set_edit_panel(self, panelname):
        """Switches the current edit panel to another.
        Argument:
            panelname: String, the name of the panel.
        """

        if self.edit_panel != panelname:
            self.edit_panel = panelname
            Clock.schedule_once(lambda *dt: self.update_edit_panel())
        elif self.edit_panel == 'main':
            self.edit_panel_object.refresh_buttons()

    def export(self):
        """Switches to export screen."""

        if self.photos:
            app = App.get_running_app()
            app.export_target = self.target
            app.export_type = self.type
            app.show_export()

    def drop_widget(self, fullpath, position, dropped_type='file', aspect=1):
        """Dummy function.  Here because the app can possibly call this function for any screen."""
        pass

    def text_input_active(self):
        """Detects if any text input fields are currently active (being typed in).
        Returns: True or False
        """

        input_active = False
        for widget in self.walk(restrict=True):
            if widget.__class__.__name__ == 'NormalInput' or widget.__class__.__name__ == 'FloatInput' or widget.__class__.__name__ == 'IntegerInput':
                if widget.focus:
                    input_active = True
                    break
        return input_active

    def has_popup(self):
        """Detects if the current screen has a popup active.
        Returns: True or False
        """

        if self.popup:
            if self.popup.open:
                return True
        return False

    def dismiss_popup(self, *_):
        """Close a currently open popup for this screen."""

        if self.popup:
            self.popup.dismiss()
            self.popup = None

    def dismiss_extra(self):
        """Deactivates fullscreen mode on the video viewer if applicable.
        Returns: True if it was deactivated, False if not.
        """

        if self.encoding:
            self.cancel_encode()
            return True
        if self.edit_panel != 'main':
            self.set_edit_panel('main')
            return True
        if self.viewer.fullscreen:
            self.viewer.stop()
            return True
        return False

    def key(self, key):
        """Handles keyboard shortcuts, performs the actions needed.
        Argument:
            key: The name of the key command to perform.
        """

        if self.text_input_active():
            pass
        else:
            if not self.popup or (not self.popup.open):
                if key == 'left' or key == 'up':
                    self.previous_photo()
                if key == 'right' or key == 'down':
                    self.next_photo()
                if key == 'enter':
                    if self.viewer:
                        self.viewer.fullscreen = not self.viewer.fullscreen
                if key == 'space':
                    self.set_favorite()
                if key == 'delete':
                    self.delete()
                if key == 'f2':
                    self.show_info_panel()
                if key == 'f3':
                    self.show_edit_panel()
                if key == 'f4':
                    self.show_tags_panel()
            elif self.popup and self.popup.open:
                if key == 'enter':
                    self.popup.content.dispatch('on_answer', 'yes')

    def next_photo(self):
        """Changes the viewed photo to the next photo in the album index."""

        current_photo_index = self.current_photo_index()
        if current_photo_index == len(self.photos) - 1:
            next_photo_index = 0
        else:
            next_photo_index = current_photo_index + 1
        new_photo = self.photos[next_photo_index]
        self.fullpath = new_photo[0]
        self.photo = os.path.join(new_photo[2], new_photo[0])
        self.scroll_photolist()

    def previous_photo(self):
        """Changes the viewed photo to the previous photo in the album index."""

        current_photo_index = self.current_photo_index()
        new_photo = self.photos[current_photo_index-1]
        self.fullpath = new_photo[0]
        self.photo = os.path.join(new_photo[2], new_photo[0])
        self.scroll_photolist()

    def set_favorite(self):
        """Toggles the currently viewed photo as favorite."""

        app = App.get_running_app()
        if not app.database_scanning:
            if self.target != 'Favorite':
                app = App.get_running_app()
                app.Tag.toggle(self.fullpath, 'favorite')
                photo_info = app.Photo.exist(self.fullpath)
                self.photos[self.current_photo_index()] = photo_info
                self.update_tags()
                self.refresh_all()
                self.viewer.favorite = self.favorite

    def delete(self):
        """Begins the delete process.  Just calls 'delete_selected_confirm'.
        Not really necessary, but is here to mirror the screenDatabase screen delete function.
        """

        self.delete_selected_confirm()

    def delete_selected_confirm(self):
        """Creates a delete confirmation popup and opens it."""

        if self.type == 'Album':
            content = ConfirmPopup(text='Remove This Photo From The Album "'+self.target+'"?', yes_text='Remove', no_text="Don't Remove", warn_yes=True)
        elif self.type == 'Tag':
            content = ConfirmPopup(text='Remove The Tag "'+self.target+'" From Selected Photo?', yes_text='Remove', no_text="Don't Remove", warn_yes=True)
        else:
            content = ConfirmPopup(text='Delete The Selected File?', yes_text='Delete', no_text="Don't Delete", warn_yes=True)
        app = App.get_running_app()
        content.bind(on_answer=self.delete_selected_answer)
        self.popup = NormalPopup(title='Confirm Delete', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
        self.popup.open()

    def delete_selected_answer(self, instance, answer):
        """Final step of the file delete process, if the answer was 'yes' will delete the selected files.
        Arguments:
            instance: The widget that called this command.
            answer: String, 'yes' if confirm, anything else on deny.
        """

        del instance
        if answer == 'yes':
            app = App.get_running_app()
            self.viewer.stop()
            fullpath = self.fullpath
            filename = self.photo
            if self.type == 'Tag':
                app.Tag.remove(fullpath, self.target, message=True)
                deleted = True
            else:
                photo_info = app.Photo.exist(fullpath)
                deleted = app.Photo.delete_file(fullpath, filename, message=True)
                if deleted:
                    if photo_info:
                        app.update_photoinfo(folders=photo_info[1])
            if deleted:
                app.photos.commit()
                if len(self.photos) == 1:
                    app.show_database()
                else:
                    self.next_photo()
                    Cache.remove('kv.loader')
                    self.cache_nearby_images()
                    #Cache.remove('kv.image')
                    #Cache.remove('kv.texture')
                    self.update_tags()
                    self.update_treeview()
        self.dismiss_popup()

    def current_photo_index(self):
        """Determines the index of the currently viewed photo in the album photos.
        Returns: Integer index value.
        """

        for index, photo in enumerate(self.photos):
            if photo[0] == self.fullpath:
                return index
        return 0

    def add_to_tag(self, tag_name):
        """Adds a tag to the currently viewed photo.
        Arguments:
            tag_name: Tag to add to current photo.
        """

        tag_name = tag_name.strip(' ')
        if tag_name:
            app = App.get_running_app()
            app.Tag.add(self.fullpath, tag_name)
            self.update_tags()
            if tag_name == 'favorite':
                self.update_treeview()

    def can_add_tag(self, tag_name):
        """Checks if a new tag can be created.
        Argument:
            tag_name: The tag name to check.
        Returns: True or False.
        """

        app = App.get_running_app()
        tag = app.session.query(Tag).filter_by(name=tag_name).first()

        if tag_name and (tag_name.lower() != 'favorite') and (tag is not None):
            return True
        else:
            return False

    def add_tag(self):
        """Adds the current input tag to the app tags."""

        app = App.get_running_app()
        tag_input = self.ids['newTag']
        tag_name = tag_input.text
        tag_name = tag_name.lower().strip(' ')
        app.Tag.create(tag_name)
        tag_input.text = ''
        self.update_tags()

    def update_tags(self):
        """Reads all tags from the current image, and all app tags and refreshes the tag list in the tags panel."""

        app = App.get_running_app()
        display_tags = self.ids['panelDisplayTags']
        display_tags.clear_widgets()
        photo = app.session.query(Photo).filter_by(id=app.target).first()
        self.photo = str(photo.id)
        if photo:
            tags = photo.tags
            if 'favorite' in tags:
                self.favorite = True
            else:
                self.favorite = False
            for tag in tags:
                    display_tags.add_widget(NormalLabel(text=tag.name, size_hint_x=1))
                    display_tags.add_widget(self.makeScreenAlbum.
                                            makeRemoveFromTagButton(to_remove=tag.name, remove_from=photo.new_full_filename(), owner=self))

        tag_list = self.ids['panelTags']
        tag_list.clear_widgets()
        tag_list.add_widget(self.makeScreenAlbum.
                            makeTagSelectButton(type='Tag', text='favorite', target='favorite', owner=self))
        tag_list.add_widget(ShortLabel())
        for tag in app.session.query(Tag).order_by(Tag.name):
            tag_list.add_widget(self.makeScreenAlbum.
                                makeTagSelectButton(type='Tag', text=tag.name, target=str(tag.id), owner=self))
            tag_list.add_widget(self.makeScreenAlbum.
                                makeRemoveTagButton(to_remove=tag.name, owner=self))

    def fullscreen(self):
        """Tells the viewer to switch to fullscreen mode."""

        if self.viewer:
            self.viewer.fullscreen = True

    def on_photo(self, *_):
        """Called when a new photo is viewed.
        Sets up the photo viewer widget and updates all necessary settings."""

        if self.viewer:
            self.viewer.stop()  #Ensure that an old video is no longer playing.
            self.viewer.close()
        app = App.get_running_app()
        app.fullpath = self.fullpath
        app.photo = self.photo
        self.update_tags()

        #Set up photo viewer
        container = self.ids['photoViewerContainer']
        container.clear_widgets()
        self.photoinfo = app.session.query(Photo).filter_by(id=self.photo).first()
        if self.photoinfo:
            self.orientation = self.photoinfo.orientation
        else:
            self.orientation = 1
            self.photoinfo = app.null_image()
        if self.orientation == 3 or self.orientation == 4:
            self.angle = 180
        elif self.orientation == 5 or self.orientation == 6:
            self.angle = 270
        elif self.orientation == 7 or self.orientation == 8:
            self.angle = 90
        else:
            self.angle = 0
        if self.orientation in [2, 4, 5, 7]:
            self.mirror = True
        else:
            self.mirror = False

        if self.photoinfo.is_photo():
            #a photo is selected
            self.view_image = True
            if app.canprint():
                print_button = self.ids['printButton']
                print_button.disabled = False
            if not self.photo:
                self.photo = 'data/null.jpg'
            self.viewer = self.makeScreenAlbum.\
                makePhotoViewer(favorite=self.favorite, angle=self.angle, mirror=self.mirror, photo_id=str(self.photoinfo.id), file=self.photoinfo.new_full_filename(),photoinfo=self.photoinfo.dict())
            container.add_widget(self.viewer)
            self.refresh_photoinfo_simple()
            self.refresh_photoinfo_full()
        else:
            #a video is selected
            self.view_image = False
            if app.canprint():
                print_button = self.ids['printButton']
                print_button.disabled = True
            if not self.photo:
                self.photo = 'data/null.jpg'
            self.viewer = self.makeScreenAlbum.\
                makeVideoViewer(favorite=self.favorite, angle=self.angle, mirror=self.mirror, file=self.photoinfo.new_full_filename(), photoinfo=self.photoinfo.dict())
            container.add_widget(self.viewer)
            self.refresh_photoinfo_simple()

        app.refresh_photo(self.fullpath)
        if app.config.getboolean("Settings", "precache"):
            self.imagecache = threading.Thread(target=self.cache_nearby_images)
            self.imagecache.start()
        self.set_edit_panel('main')  #Clear the edit panel
        #self.ids['album'].selected = self.fullpath

    def cache_nearby_images(self):
        """Determines the next and previous images in the list, and caches them to speed up browsing."""

        current_photo_index = self.current_photo_index()
        if current_photo_index == len(self.photos) -1:
            next_photo_index = 0
        else:
            next_photo_index = current_photo_index + 1
        next_photo_info = self.photos[next_photo_index]
        prev_photo_info = self.photos[current_photo_index-1]
        next_photo_filename = os.path.join(next_photo_info[2], next_photo_info[0])
        prev_photo_filename = os.path.join(prev_photo_info[2], prev_photo_info[0])
        if next_photo_filename != self.photo and os.path.splitext(next_photo_filename)[1].lower() in imagetypes:
            try:
                if os.path.splitext(next_photo_filename)[1].lower() == '.bmp':
                    next_photo = ImageLoaderPIL(next_photo_filename)
                else:
                    next_photo = Loader.image(next_photo_filename)
            except:
                pass
        if prev_photo_filename != self.photo and os.path.splitext(prev_photo_filename)[1].lower() in imagetypes:
            try:
                if os.path.splitext(prev_photo_filename)[1].lower() == '.bmp':
                    next_photo = ImageLoaderPIL(prev_photo_filename)
                else:
                    prev_photo = Loader.image(prev_photo_filename)
            except:
                pass

    def show_selected(self):
        album_container = self.ids['albumContainer']
        album = self.ids['album']
        selected = self.fullpath
        data = album_container.data
        current_photo = None
        for i, node in enumerate(data):
            if node['fullpath'] == selected:
                current_photo = node
                break
        if current_photo is not None:
            album.selected = current_photo

    def scroll_photolist(self):
        """Scroll the right-side photo list to the current active photo."""

        photolist = self.ids['albumContainer']
        self.show_selected()
        photolist.scroll_to_selected()

    def refresh_all(self, *_):
        self.refresh_photolist()
        self.refresh_photoview()

    def refresh_photolist(self):
        """Reloads and sorts the photo list"""

        app = App.get_running_app()

        #Get photo list
        self.photos = []
        if self.type == 'Album':
            self.folder_title = 'Album: "'+self.target+'"'
            for albuminfo in app.albums:
                if albuminfo['name'] == self.target:
                    photo_paths = albuminfo['photos']
                    for fullpath in photo_paths:
                        photoinfo = app.Photo.exist(fullpath)
                        if photoinfo:
                            self.photos.append(photoinfo)
        elif self.type == 'Tag':
            self.folder_title = 'Tagged As: "'+self.target+'"'
            self.photos = app.Tag.photos(self.target)
        else:
            self.folder_title = 'Folder: "'+self.target+'"'
            self.photo = app.session.query(Photo).filter_by(id=self.target).first()
            self.photos = self.photo.folder.photos

        #Sort photos
        if self.sort_method == 'Imported':
            sorted_photos = sorted(self.photos, key=lambda x: x.import_date, reverse=self.sort_reverse)
        elif self.sort_method == 'Modified':
            sorted_photos = sorted(self.photos, key=lambda x: x.modify_date, reverse=self.sort_reverse)
        elif self.sort_method == 'Owner':
            sorted_photos = sorted(self.photos, key=lambda x: x.owner, reverse=self.sort_reverse)
        elif self.sort_method == 'Name':
            sorted_photos = sorted(self.photos, key=lambda x: os.original_file, reverse=self.sort_reverse)
        else:
            sorted_photos = sorted(self.photos, key=lambda x: x.original_date, reverse=self.sort_reverse)
        self.photos = sorted_photos

    def refresh_photoview(self):
        #refresh recycleview
        photolist = self.ids['albumContainer']
        photodatas = []
        for photo in self.photos:
            photodata = {}
            source = os.path.join(photo[2], photo[0])
            photodata['text'] = os.path.basename(photo[0])
            photodata['source'] = source
            photodata['photoinfo'] = photo
            photodata['owner'] = self
            photodata['favorite'] = True if 'favorite' in photo[8].split(',') else False
            photodata['fullpath'] = photo[0]
            photodata['video'] = os.path.splitext(source)[1].lower() in movietypes
            photodata['selectable'] = True
            #if self.fullpath == photo[0]:
            #    photodata['selected'] = True
            #else:
            #    photodata['selected'] = False
            photodatas.append(photodata)
        photolist.data = photodatas

    def full_photo_refresh(self):
        app = App.get_running_app()
        app.refresh_photo(self.fullpath, force=True)
        self.on_photo()

    def refresh_photoinfo_simple(self):
        """Displays the basic info for the current photo in the photo info right tab."""

        app = App.get_running_app()

        #Clear old info
        info_panel = self.ids['panelInfo']
        nodes = list(info_panel.iterate_all_nodes())
        for node in nodes:
            info_panel.remove_node(node)

        #Add basic info
        photoinfo = app.Photo.exist(self.fullpath)
        if not photoinfo:
            return
        full_filename = os.path.join(photoinfo[2], photoinfo[0])
        filename = os.path.basename(photoinfo[0])
        self.makeScreenAlbum.makeTreeViewInfo
        info_panel.add_node(self.makeScreenAlbum.
                            makeTreeViewInfo(title='Filename: ' + filename))
        path = os.path.join(photoinfo[2], photoinfo[1])
        info_panel.add_node(self.makeScreenAlbum.
                            makeTreeViewInfo(title='Path: ' + path))
        database_folder = photoinfo[2]
        info_panel.add_node(self.makeScreenAlbum.
                            makeTreeViewInfo(title='Database: ' + database_folder))
        import_date = datetime.datetime.fromtimestamp(photoinfo[6]).strftime('%Y-%m-%d, %I:%M%p')
        info_panel.add_node(self.makeScreenAlbum.
                            makeTreeViewInfo(title='Import Date: ' + import_date))
        modified_date = datetime.datetime.fromtimestamp(photoinfo[7]).strftime('%Y-%m-%d, %I:%M%p')
        info_panel.add_node(self.makeScreenAlbum.
                            makeTreeViewInfo(title='Modified Date: ' + modified_date))
        if os.path.exists(full_filename):
            file_size = format_size(int(os.path.getsize(full_filename)))
        else:
            file_size = format_size(photoinfo[4])
        info_panel.add_node(self.makeScreenAlbum.
                            makeTreeViewInfo(title='File Size: ' + file_size))

    def refresh_photoinfo_full(self, video=None):
        """Displays all the info for the current photo in the photo info right tab."""

        info_panel = self.ids['panelInfo']
        app = App.get_running_app()
        container = self.ids['photoViewerContainer']

        if not self.view_image:
            if video:
                length = time_index(video.duration)
                info_panel.add_node(self.makeScreenAlbum.
                                    makeTreeViewInfo(title='Duration: ' + length))
                self.image_x, self.image_y = video.texture.size
                resolution = str(self.image_x) + ' * ' + str(self.image_y)
                megapixels = round(((self.image_x * self.image_y) / 1000000), 2)
                info_panel.add_node(self.makeScreenAlbum.
                                    makeTreeViewInfo(title='Resolution: ' + str(megapixels) + 'MP (' + resolution + ')'))
        else:
            #Add resolution info
            try:
                pil_image = Image.open(self.photo)
                exif = pil_image._getexif()
            except:
                pil_image = False
                exif = []
            if pil_image:
                self.image_x, self.image_y = pil_image.size
                wrapper_size = container.size
                if wrapper_size[0] > 0:
                    xscale = self.image_x/wrapper_size[0]
                else:
                    xscale = 1
                if wrapper_size[1] > 0:
                    yscale = self.image_y/wrapper_size[1]
                else:
                    yscale = 1
                if xscale > yscale:
                    scale_max = xscale
                else:
                    scale_max = yscale
                if scale_max < 2 or to_bool(app.config.get("Settings", "lowmem")):
                    scale_max = 2
                self.viewer.scale_max = scale_max
                resolution = str(self.image_x) + ' * ' + str(self.image_y)
                megapixels = round(((self.image_x * self.image_y) / 1000000), 2)
                info_panel.add_node(self.makeScreenAlbum.
                                    makeTreeViewInfo(title='Resolution: ' + str(megapixels) + 'MP (' + resolution + ')'))
            else:
                self.image_x = 0
                self.image_y = 0

            #Add exif info
            if exif:
                if 271 in exif:
                    camera_type = exif[271]+' '+exif[272]
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='Camera: ' + camera_type))
                if 33432 in exif:
                    copyright = exif[33432]
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='Copyright: ' + copyright))
                if 36867 in exif:
                    camera_date = exif[36867]
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='Date Taken: ' + camera_date))
                if 33434 in exif:
                    exposure = exif[33434]
                    camera_exposure = str(exposure[0]/exposure[1])+'seconds'
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='Exposure Time: ' + camera_exposure))
                if 37377 in exif:
                    camera_shutter_speed = str(exif[37377][0]/exif[37377][1])
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='Shutter Speed: ' + camera_shutter_speed))
                if 33437 in exif:
                    f_stop = exif[33437]
                    camera_f = str(f_stop[0]/f_stop[1])
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='F Stop: ' + camera_f))
                if 37378 in exif:
                    camera_aperture = str(exif[37378][0]/exif[37378][0])
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='Aperture: ' + camera_aperture))
                if 34855 in exif:
                    camera_iso = str(exif[34855])
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='ISO Level: ' + camera_iso))
                if 37385 in exif:
                    flash = bin(exif[37385])[2:].zfill(8)
                    camera_flash = 'Not Used' if flash[1] == '0' else 'Used'
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='Flash: ' + str(camera_flash)))
                if 37386 in exif:
                    focal_length = str(exif[37386][0]/exif[37386][1])+'mm'
                    if 41989 in exif:
                        film_focal = exif[41989]
                        if film_focal != 0:
                            focal_length = focal_length+' ('+str(film_focal)+' 35mm equiv.)'
                    info_panel.add_node(self.makeScreenAlbum.
                                        makeTreeViewInfo(title='Focal Length: ' + focal_length))
                if 41988 in exif:
                    digital_zoom = exif[41988]
                    if digital_zoom[0] != 0:
                        digital_zoom_amount = str(round(digital_zoom[0]/digital_zoom[1], 2))+'X'
                        info_panel.add_node(self.makeScreenAlbum.
                                            makeTreeViewInfo(title='Digital Zoom: ' + digital_zoom_amount))
                if 34850 in exif:
                    exposure_program = exif[34850]
                    if exposure_program > 0:
                        if exposure_program == 1:
                            program_name = 'Manual'
                        elif exposure_program == 2:
                            program_name = 'Normal'
                        elif exposure_program == 3:
                            program_name = 'Aperture Priority'
                        elif exposure_program == 4:
                            program_name = 'Shutter Priority'
                        elif exposure_program == 5:
                            program_name = 'Creative Program'
                        elif exposure_program == 6:
                            program_name = 'Action Program'
                        elif exposure_program == 7:
                            program_name = 'Portrait'
                        else:
                            program_name = 'Landscape'
                        info_panel.add_node(self.makeScreenAlbum.
                                            makeTreeViewInfo(title='Exposure Mode: ' + program_name))

    def resort_method(self, method):
        """Sets the album sort method.
        Argument:
            method: String, the sort method to use
        """

        self.sort_method = method
        app = App.get_running_app()
        app.config.set('Sorting', 'album_sort', method)
        self.refresh_all()
        Clock.schedule_once(lambda *dt: self.scroll_photolist())

    def resort_reverse(self, reverse):
        """Sets the album sort reverse.
        Argument:
            reverse: String, if 'down', reverse will be enabled, disabled on any other string.
        """

        app = App.get_running_app()
        sort_reverse = True if reverse == 'down' else False
        app.config.set('Sorting', 'album_sort_reverse', sort_reverse)
        self.sort_reverse = sort_reverse
        self.refresh_all()
        Clock.schedule_once(lambda *dt: self.scroll_photolist())

    def add_program(self):
        """Add a new external program to the programs panel."""

        app = App.get_running_app()
        app.program_add('Program Name', 'command', '%i')
        self.edit_panel_object.update_programs(expand=True)

    def on_leave(self):
        """Called when the screen is left.  Clean up some things."""

        if self.viewer:
            self.viewer.stop()
        app = App.get_running_app()
        right_panel = self.ids['rightpanel']
        #right_panel.width = app.right_panel_width()
        right_panel.hidden = True
        self.view_panel = ''
        self.show_left_panel()

    def clear_cache(self):
        """Clears cached images and thumbnails, the app will redraw all images.
        Also redraws photolist and photo viewer."""

        if self.viewer:
            if self.view_image:
                photoimage = self.viewer.ids['image']
                photoimage.source = ''
                photoimage.source = self.photo
        Cache.remove('kv.loader')
        Cache.remove('kv.image')
        Cache.remove('kv.texture')
        #self.on_photo()
        self.update_tags()
        self.refresh_all()

    def update_treeview(self):
        """Called by delete buttons."""

        self.on_enter()
        self.on_photo()

    def on_enter(self):
        """Called when the screen is entered.  Set up variables and widgets, and prepare to view images."""

        self.ffmpeg = ffmpeg
        self.opencv = opencv
        app = App.get_running_app()
        self.ids['leftpanel'].width = app.left_panel_width()
        right_panel = self.ids['rightpanel']
        right_panel.hidden = True
        self.view_panel = ''
        self.show_left_panel()

        #set up printing button
        if not app.canprint():
            self.canprint = False
        else:
            self.canprint = True

        #import variables
        self.target = app.target
        self.type = app.type

        #set up sort buttons
        self.sort_dropdown = AlbumSortDropDown()
        self.sort_dropdown.bind(on_select=lambda instance, x: self.resort_method(x))
        self.sort_method = app.config.get('Sorting', 'album_sort')
        self.sort_reverse = to_bool(app.config.get('Sorting', 'album_sort_reverse'))

        #refresh views
        self.update_tags()
        self.refresh_photolist()

        if self.photos:
            check_fullpath = ''
            check_photo = ''
            if app.fullpath:
                check_fullpath = app.fullpath
                check_photo = app.photo
            elif self.fullpath:
                check_fullpath = self.fullpath
                check_photo = self.photo

            photo_in_list = False
            for photoinfo in self.photos:
                if photoinfo.full_path == check_fullpath:
                    photo_in_list = True
                    break
            if photo_in_list:
                self.fullpath = check_fullpath
                self.photo = check_photo
            else:
                photoinfo = self.photos.first()
                self.fullpath = photoinfo.full_path
                self.photo = photoinfo.new_full_filename()

            Clock.schedule_once(lambda *dt: self.scroll_photolist())
        self.refresh_photoview()

        #reset edit panel
        self.encoding = False
        self.cancel_encoding = False
        self.edit_panel = 'main'
        Clock.schedule_once(lambda *dt: self.update_edit_panel())

    def update_edit_panel(self):
        """Set up the edit panel with the current preset."""

        if self.viewer and isfile2(self.photo):
            self.viewer.stop()
            if self.edit_panel_object:
                self.edit_panel_object.save_last()
            self.viewer.edit_mode = self.edit_panel
            edit_panel_container = self.ids['panelEdit']
            if self.edit_panel == 'main':
                self.edit_panel_object = self.makeScreenAlbum.\
                    makeEditMain(owner=self)
                self.edit_panel_object.update_programs()
                self.viewer.bypass = False
            else:
                self.viewer.bypass = True
                self.viewer.stop()
                if self.edit_panel == 'color':
                    self.edit_panel_object = self.makeScreenAlbum.\
                        makeEditColorImage(owner=self)
                    self.viewer.edit_image.bind(histogram=self.edit_panel_object.draw_histogram)
                elif self.edit_panel == 'advanced':
                    self.edit_panel_object = self.makeScreenAlbum.\
                        makeEditColorImageAdvanced(owner=self)
                    self.viewer.edit_image.bind(histogram=self.edit_panel_object.draw_histogram)
                elif self.edit_panel == 'filter':
                    self.edit_panel_object = self.makeScreenAlbum.\
                        makeEditFilterImage(owner=self)
                elif self.edit_panel == 'border':
                    self.edit_panel_object = self.makeScreenAlbum.makeEditBorderImage(owner=self)
                elif self.edit_panel == 'denoise':
                    if opencv:
                        self.edit_panel_object = self.makeScreenAlbum.\
                            makeEditDenoiseImage(owner=self, imagefile=self.photo, image_x=self.viewer.edit_image.original_width, image_y=self.viewer.edit_image.original_height)
                    else:
                        self.edit_panel = 'main'
                        app = App.get_running_app()
                        app.message("Could Not Denoise, OpenCV Not Found")
                elif self.edit_panel == 'crop':
                    self.edit_panel_object = self.makeScreenAlbum.\
                        makeEditCropImage(owner=self, image_x=self.viewer.edit_image.original_width,
                                                           image_y=self.viewer.edit_image.original_height)
                    self.viewer.edit_image.crop_controls = self.edit_panel_object
                elif self.edit_panel == 'rotate':
                    self.edit_panel_object = self.makeScreenAlbum.\
                        makeEditRotateImage(owner=self)
                elif self.edit_panel == 'convert':
                    if self.view_image:
                        self.edit_panel_object = self.makeScreenAlbum.\
                            makeEditConvertImage(owner=self)
                    else:
                        self.edit_panel_object = self.makeScreenAlbum.\
                            makeEditConvertVideo(owner=self)
            edit_panel_container.change_panel(self.edit_panel_object)
        else:
            if self.edit_panel_object:
                self.edit_panel_object.save_last()
            self.viewer.edit_mode = self.edit_panel
            edit_panel_container = self.ids['panelEdit']
            edit_panel_container.change_panel(None)
            self.edit_panel_object = self.makeScreenAlbum.\
                makeEditNone(owner=self)

    def save_edit(self):
        if self.view_image:
            self.save_image()
        else:
            self.save_video()

    def cancel_save_video(self, *_):
        """Signal to cancel the video processing process."""

        self.encoding = False
        self.cancel_encoding = True
        if self.encoding_process_thread:
            self.encoding_process_thread.kill()
        app = App.get_running_app()
        app.message("Canceled video processing.")

    def save_video(self):
        app = App.get_running_app()
        app.save_encoding_preset()
        self.viewer.stop()

        # Create popup to show progress
        self.cancel_encoding = False
        self.popup = ScanningPopup(title='Processing Video', auto_dismiss=False, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
        self.popup.scanning_text = ''
        self.popup.open()
        encoding_button = self.popup.ids['scanningButton']
        encoding_button.bind(on_press=self.cancel_save_video)

        # Start encoding thread
        self.encodingthread = threading.Thread(target=self.save_video_process)
        self.encodingthread.start()

    def failed_encode(self, message):
        app = App.get_running_app()
        self.cancel_save_video()
        self.dismiss_popup()
        self.encoding = False
        app.popup_message(text=message, title='Warning')

    def save_video_process(self):
        self.viewer.stop()
        app = App.get_running_app()
        input_file = self.photo
        input_file_folder, input_filename = os.path.split(input_file)
        output_file_folder = input_file_folder+os.path.sep+'reencode'
        encoding_settings = None
        preset_name = app.selected_encoder_preset
        for preset in app.encoding_presets:
            if preset['name'] == preset_name:
                encoding_settings = preset
        if not encoding_settings:
            encoding_settings = app.encoding_presets[0]

        if not os.path.isdir(output_file_folder):
            try:
                os.makedirs(output_file_folder)
            except:
                self.failed_encode('File not encoded, could not create temporary "reencode" folder')
                return
        edit_image = self.viewer.edit_image
        start_point = self.viewer.start_point
        end_point = self.viewer.end_point
        pixel_format = edit_image.pixel_format
        input_size = [edit_image.original_width, edit_image.original_height]
        length = edit_image.length
        length = length * (end_point - start_point)
        edit_image.start_video_convert()
        start_seconds = edit_image.start_seconds
        frame_number = 1
        framerate = edit_image.framerate
        duration = edit_image.length
        self.total_frames = (duration * (end_point - start_point)) * (framerate[0] / framerate[1])
        start_frame = int(self.total_frames * start_point)
        #change
        mpegCommand = MpegCommand()
        mpegCommand.set_input_folder(input_file_folder)
        mpegCommand.set_input_filename(input_filename)
        mpegCommand.set_output_file_folder(output_file_folder)
        mpegCommand.set_input_size(input_size)
        mpegCommand.set_noaudio(True)
        mpegCommand.set_input_file('-')
        mpegCommand.set_input_images(True)
        mpegCommand.set_input_framerate(framerate)
        mpegCommand.set_input_pixel_format(pixel_format)
        mpegCommand.set_encoding_settings(encoding_settings)
        command_valid, command, output_filename = mpegCommand.ffmpeg_command()
        ######################################################################
        if not command_valid:
            self.failed_encode('Command not valid: '+command)
            return
        output_file = output_file_folder+os.path.sep+output_filename
        deleted = self.delete_output(output_file)
        if not deleted:
            self.failed_encode('File not encoded, temporary file already exists, could not delete')
            return
        #command = 'ffmpeg -f image2pipe -vcodec mjpeg -i "-" -vcodec libx264 -r 30 -b:v 8000k "'+output_file+'"'
        print(command)

        start_time = time.time()
        #used to have shell=True in arguments, is it still needed?
        self.encoding_process_thread = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
        # Poll process for new output until finished
        while True:
            if self.cancel_encoding:
                self.dismiss_popup()
                self.encoding_process_thread.kill()
                deleted = self.delete_output(output_file)
                if not os.listdir(output_file_folder):
                    os.rmdir(output_file_folder)
                return
            frameinfo = edit_image.get_converted_frame()
            if frameinfo is None:
                #finished encoding
                break
            frame, pts = frameinfo
            try:
                frame.save(self.encoding_process_thread.stdin, 'JPEG')
            except:
                if not self.cancel_encoding:
                    lines = self.encoding_process_thread.stdout.readlines()
                    for line in lines:
                        sys.stdout.write(line)
                        sys.stdout.flush()
                    deleted = self.delete_output(output_file)
                    if not os.listdir(output_file_folder):
                        try:
                            os.rmdir(output_file_folder)
                        except:
                            pass
                    self.failed_encode('Ffmpeg shut down, failed encoding on frame: '+str(frame_number))
                    return
            #output_file = output_file_folder+os.path.sep+'image'+str(frame_number).zfill(4)+'.jpg'
            #frame.save(output_file, "JPEG", quality=95)
            frame_number = frame_number+1
            scanning_percentage = ((pts - start_seconds)/length) * 95
            self.popup.scanning_percentage = scanning_percentage
            elapsed_time = time.time() - start_time

            try:
                percentage_remaining = 95 - scanning_percentage
                seconds_left = (elapsed_time * percentage_remaining) / scanning_percentage
                time_done = time_index(elapsed_time)
                time_remaining = time_index(seconds_left)
                time_text = "  Time: " + time_done + "  Remaining: " + time_remaining
            except:
                time_text = ""
            self.popup.scanning_text = str(int(scanning_percentage))+"%"+time_text

        self.encoding_process_thread.stdin.close()
        self.encoding_process_thread.wait()

        #output = self.encoding_process_thread.communicate()[0]
        exit_code = self.encoding_process_thread.returncode

        if exit_code == 0:
            #encoding first file completed, add audio
            mpegAudioCommand = MpegAudioCommand()

            mpegAudioCommand.set_video_input_folder(output_file_folder)
            mpegAudioCommand.set_video_input_filename(output_filename)
            mpegAudioCommand.set_audio_input_folder(input_file_folder)
            mpegAudioCommand.set_audio_input_filename(input_filename)
            mpegAudioCommand.set_output_file_folder(output_file_folder)
            mpegAudioCommand.set_encoding_settings(encoding_settings)
            mpegAudioCommand.set_start(start_seconds)
            command_valid, command, output_temp_filename = mpegAudioCommand.mpeg_audio_command()

            #command_valid, command, output_temp_filename = self.get_ffmpeg_audio_command(output_file_folder, output_filename, input_file_folder, input_filename, output_file_folder, encoding_settings=encoding_settings, start=start_seconds)
            output_temp_file = output_file_folder + os.path.sep + output_temp_filename

            print(command)
            #used to have shell=True in arguments... is it still needed?
            self.encoding_process_thread = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)
            #Poll process for new output until finished
            deleted = self.delete_output(output_temp_file)
            if not deleted:
                self.failed_encode('File not encoded, temporary file already existed and could not be replaced')
                return
            while True:
                if self.cancel_encoding:
                    self.dismiss_popup()
                    self.encoding_process_thread.kill()
                    deleted = self.delete_output(output_file)
                    deleted = self.delete_output(output_temp_file)
                    if not os.listdir(output_file_folder):
                        try:
                            os.rmdir(output_file_folder)
                        except:
                            pass
                    return

                nextline = self.encoding_process_thread.stdout.readline()
                if nextline == '' and self.encoding_process_thread.poll() is not None:
                    break
                if nextline.startswith('frame= '):
                    self.current_frame = int(nextline.split('frame=')[1].split('fps=')[0].strip())
                    scanning_percentage = 95 + ((self.current_frame - start_frame) / self.total_frames * 5)
                    self.popup.scanning_percentage = scanning_percentage
                    elapsed_time = time.time() - start_time

                    try:
                        percentage_remaining = 95 - scanning_percentage
                        seconds_left = (elapsed_time * percentage_remaining) / scanning_percentage
                        time_done = time_index(elapsed_time)
                        time_remaining = time_index(seconds_left)
                        time_text = "  Time: " + time_done + "  Remaining: " + time_remaining
                    except:
                        time_text = ""
                    self.popup.scanning_text = str(int(scanning_percentage)) + "%" + time_text

                sys.stdout.write(nextline)
                sys.stdout.flush()

            output = self.encoding_process_thread.communicate()[0]
            exit_code = self.encoding_process_thread.returncode

            #delete output_file
            deleted = self.delete_output(output_file)

            if exit_code == 0:
                #second encoding completed
                self.viewer.edit_image.close_video()

                new_original_file = input_file_folder+os.path.sep+'.originals'+os.path.sep+input_filename
                if not os.path.isdir(input_file_folder+os.path.sep+'.originals'):
                    os.makedirs(input_file_folder+os.path.sep+'.originals')
                new_encoded_file = input_file_folder+os.path.sep+output_filename

                new_photoinfo = list(self.photoinfo)
                #check if original file has been backed up already
                if not os.path.isfile(self.photoinfo[10]):
                    #original file exists
                    try:
                        os.rename(input_file, new_original_file)
                    except:
                        self.failed_encode('Could not replace video, converted video left in "reencode" subfolder')
                        return
                    new_photoinfo[10] = new_original_file
                else:
                    deleted = self.delete_output(input_file)
                    if not deleted:
                        self.failed_encode('Could not replace video, converted video left in "reencode" subfolder')
                        return
                try:
                    os.rename(output_temp_file, new_encoded_file)
                except:
                    self.failed_encode('Could not replace video, original file may be deleted, converted video left in "reencode" subfolder')
                    return

                if not os.listdir(output_file_folder):
                    os.rmdir(output_file_folder)

                #update screenDatabase
                extension = os.path.splitext(new_encoded_file)[1]
                new_photoinfo[0] = os.path.splitext(self.photoinfo[0])[0]+extension  #fix extension
                new_photoinfo[7] = int(os.path.getmtime(new_encoded_file))  #update modified date
                new_photoinfo[9] = 1  #set edited

                # regenerate thumbnail
                app.Photo.thumbnail_update(self.photoinfo[0], self.photoinfo[2], self.photoinfo[7], self.photoinfo[13])

                if self.photoinfo[0] != new_photoinfo[0]:
                    app.Photo.rename(self.photoinfo[Photo.FULLPATH], new_photoinfo[Photo.FULLPATH], new_photoinfo[Photo.FOLDER])
                app.Photo.update(new_photoinfo)

                self.dismiss_popup()

                # reload video in ui
                self.photoinfo = new_photoinfo
                self.fullpath = local_path(new_photoinfo[0])
                #self.photo = os.path.join(local_path(new_photoinfo[2]), local_path(new_photoinfo[0]))
                Clock.schedule_once(lambda *dt: self.set_photo(os.path.join(local_path(new_photoinfo[2]), local_path(new_photoinfo[0]))))

                #Clock.schedule_once(lambda *dt: self.refresh_photolist())
                Clock.schedule_once(lambda x: app.message("Completed encoding file '"+self.photo+"'"))
            else:
                #failed second encode, clean up
                self.dismiss_popup()
                self.delete_output(output_file)
                self.delete_output(output_temp_file)
                if not os.listdir(output_file_folder):
                    os.rmdir(output_file_folder)
                app.popup_message(text='Second file not encoded, FFMPEG gave exit code '+str(exit_code), title='Warning')
                return
        else:
            #failed first encode, clean up
            self.failed_encode('First file not encoded, FFMPEG gave exit code '+str(exit_code))
            deleted = self.delete_output(output_file)
            if not os.listdir(output_file_folder):
                try:
                    os.rmdir(output_file_folder)
                except:
                    pass
        if self.encoding_process_thread:
            self.encoding_process_thread.kill()

        #regenerate thumbnail
        app.Photo.thumbnail_update(self.photoinfo[0], self.photoinfo[2], self.photoinfo[7], self.photoinfo[13])

        #reload photo image in ui
        Clock.schedule_once(lambda x: self.clear_cache())

        self.encoding = False
        self.set_edit_panel('main')

        #switch active video in photo list back to image
        self.show_selected()

    def save_image(self):
        """Saves any temporary edits on the currently viewed image."""

        app = App.get_running_app()

        #generate full quality image
        edit_image = self.viewer.edit_image.get_full_quality()
        exif = self.viewer.edit_image.exif
        self.viewer.stop()

        #back up old image and save new edit
        photo_file = self.photo
        backup_directory = local_path(self.photoinfo[2])+os.path.sep+local_path(self.photoinfo[1])+os.path.sep+'.originals'
        if not os.path.exists(backup_directory):
            os.mkdir(backup_directory)
        if not os.path.exists(backup_directory):
            app.popup_message(text='Could not create backup directory', title='Warning')
            return
        backup_photo_file = backup_directory+os.path.sep+os.path.basename(self.photo)
        if not os.path.isfile(photo_file):
            app.popup_message(text='Photo file no longer exists', title='Warning')
            return
        if not os.path.isfile(backup_photo_file):
            try:
                os.rename(photo_file, backup_photo_file)
            except Exception as e:
                print(e)
                pass
        if not os.path.isfile(backup_photo_file):
            app.popup_message(text='Could not create backup photo', title='Warning')
            return
        if os.path.isfile(photo_file):
            try:
                os.remove(photo_file)
            except:
                pass
        if os.path.isfile(photo_file):
            app.popup_message(text='Could not save edited photo', title='Warning')
            return
        edit_image.save(photo_file, "JPEG", quality=95, exif=exif)
        if not os.path.isfile(photo_file):
            if os.path.isfile(backup_photo_file):
                copy2(backup_photo_file, photo_file)
                app.popup_message(text='Could not save edited photo, restoring backup', title='Warning')
            else:
                app.popup_message(text='Could not save edited photo', title='Warning')
            return

        #update photo info
        self.photoinfo[10] = agnostic_path(backup_photo_file)
        self.photoinfo[13] = 1
        self.photoinfo[9] = 1
        self.photoinfo[7] = int(os.path.getmtime(photo_file))
        update_photoinfo = list(self.photoinfo)
        update_photoinfo[0] = agnostic_path(update_photoinfo[0])
        update_photoinfo[1] = agnostic_path(update_photoinfo[1])
        update_photoinfo[2] = agnostic_path(update_photoinfo[2])
        app.Photo.update(update_photoinfo)
        app.save_photoinfo(target=self.photoinfo[1], save_location=os.path.join(self.photoinfo[2], self.photoinfo[1]))

        #regenerate thumbnail
        app.Photo.thumbnail_update(self.photoinfo[0], self.photoinfo[2], self.photoinfo[7], self.photoinfo[13])

        #reload photo image in ui
        self.clear_cache()

        #close edit panel
        self.set_edit_panel('main')

        #switch active photo in photo list back to image
        self.show_selected()

        app.message("Saved edits to image")
