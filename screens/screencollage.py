import os
import random
import math
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from filebrowser import FileBrowser

from generalcommands import to_bool
from generalElements.popups.MessagePopup import MessagePopup
from generalElements.popups.NormalPopup import NormalPopup
from generalElements.popups.ConfirmPopup import ConfirmPopup
from generalElements.dropDowns.AlbumSortDropDown import AlbumSortDropDown
from generalconstants import *

from kivy.lang.builder import Builder

from screenCollage.AddRemoveDropDown import AddRemoveDropDown
from screenCollage.ColorDropDown import ColorDropDown
from screenCollage.ExpotAspectratioDropDown import ExportAspectRatioDropDown
from screenCollage.ResolutionDropDown import ResolutionDropDown
#from screenCollage.ScatterImage import ScatterImage
#from generalElements.photos.StencilViewTouch import StencilViewTouch
from screens.imageCollage import ImageCollage

Builder.load_string("""
<ScreenCollage>:
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
                text: 'Create Collage'
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
                        viewclass: 'PhotoRecycleThumb'
                        scroll_distance: 10
                        scroll_timeout: 200
                        bar_width: int(app.button_scale * .5)
                        bar_color: app.theme.scroller_selected
                        bar_inactive_color: app.theme.scroller
                        scroll_type: ['bars', 'content']
                        SelectableRecycleGrid:
                            cols: int((self.width - app.button_scale) / (app.button_scale * 3))
                            multiselect: False
                            spacing: 10
                            id: album
                            default_size: (app.button_scale * 3), (app.button_scale * 3)
            MainArea:
                size_hint: .75, 1
                orientation: 'vertical'
                AnchorLayout:
                    canvas.before:
                        Color:
                            rgba: 1-root.collage_background[0], 1-root.collage_background[1], 1-root.collage_background[2], .333
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    anchor_x: 'center'
                    anchor_y: 'center'
                    RelativeLayout:
                        size_hint: None, None
                        height: self.parent.height if (self.parent.width >= (self.parent.height * root.aspect)) else (self.parent.width / root.aspect)
                        width: int(self.height * root.aspect)
                        StencilViewTouch:
                            canvas.before:
                                Color:
                                    rgb: root.collage_background
                                Rectangle:
                                    pos: self.pos
                                    size: self.size
                            size_hint: 1, 1
                            id: collageHolder
                Header:
                    size_hint_y: None
                    height: app.button_scale
                    NormalToggle:
                        id: moveButton
                        text: '  Move  '
                        on_press: root.change_transform('move')
                        group: 'transform'
                        state: 'down'
                        size_hint_y: None
                        width: 0 if app.simple_interface else self.texture_size[0] + 20
                        opacity: 0 if app.simple_interface else 1
                        disabled: True if app.simple_interface else False
                    NormalToggle:
                        id: rotateButton
                        text: '  Rotate/Scale  '
                        on_press: root.change_transform('rotscale')
                        group: 'transform'
                        width: 0 if app.simple_interface else self.texture_size[0] + 20
                        opacity: 0 if app.simple_interface else 1
                        disabled: True if app.simple_interface else False
                    Label:
                        size_hint_x: None
                        width: 0 if app.simple_interface else app.button_scale * 2
                    MenuStarterButtonWide:
                        text: '  Add/Remove  '
                        on_release: root.add_remove.open(self)
                    MenuStarterButtonWide:
                        text: '  Background Color  '
                        on_release: root.color_select.open(self)
                    MenuStarterButtonWide:
                        text: '  Shape: '+str(root.aspect_text)+'  '
                        on_release: root.aspect_select.open(self)
                    MenuStarterButtonWide:
                        text: '  Export Size: '+root.resolution+'  '
                        on_release: root.resolution_select.open(self)
                    NormalButton:
                        text: '  Export  '
                        on_release: root.export()



""")


class ScreenCollage(Screen, ImageCollage):
    sort_reverse_button = StringProperty('normal')
    collage_background = ListProperty([0, 0, 0, 1])
    resolution = StringProperty('Medium')
    #aspect = NumericProperty(1.3333)
    aspect_text = StringProperty('4:3')
    filename = StringProperty('')
    export_scale = 1

    #Widget holder variables
    sort_dropdown = ObjectProperty()  #Holder for the sort method dropdown menu
    popup = None  #Holder for the screen's popup dialog
    resolution_select = ObjectProperty()
    color_select = ObjectProperty()
    aspect_select = ObjectProperty()
    add_remove = ObjectProperty()

    #Variables relating to the photo list view on the left
    selected = StringProperty('')  #The current folder/album/tag being displayed
    type = StringProperty('None')  #'Folder', 'Album', 'Tag'
    target = StringProperty()  #The identifier of the album/folder/tag that is being viewed
    photos = []  #Photoinfo of all photos in the album
    sort_method = StringProperty('Name')  #Current album sort method
    sort_reverse = BooleanProperty(False)
    add_collage = {}



    def delete_selected(self):
        collage = self.ids['collageHolder']
        for image in collage.children:
            if image.selected:
                collage.remove_widget(image)

    def clear_collage(self):
        collage = self.ids['collageHolder']
        collage.clear_widgets()
        self.images = []
        self.collage_background = [0, 0, 0, 1]

    def add_all(self):
        #adds all photos to the collage using a fimonacci spiral pattern
        collage = self.ids['collageHolder']
        size = (1 / (len(self.photos) ** 0.5))  #average scale of photo
        photos = list(self.photos)
        random.shuffle(photos)

        tau = (1+5**0.5)/2
        inc = (2-tau)*2*math.pi
        theta = 0

        max_x = 0
        max_y = 0
        coords = []
        offset_scale = .5
        app = App.get_running_app()
        app.message("Added "+str(len(photos))+" images.")
        #Generate basis coordinates and determine min/max
        for index in range(0, len(photos)):
            offset = (random.random()*offset_scale) - (.5*offset_scale)  #random angle variation
            r = index**0.5
            theta = theta + inc + offset
            pos_x = 0.5 + r*math.cos(theta)
            if abs(pos_x) > max_x:
                max_x = abs(pos_x)
            pos_y = 0.5 + r*math.sin(theta)
            if abs(pos_y) > max_y:
                max_y = abs(pos_y)
            coords.append((pos_x, pos_y))

        #add photos to collage
        for index, photo in enumerate(photos):
            rand_angle = random.randint(-33, 33)
            pos_x, pos_y = coords[index]
            #scale points down by max size
            pos_x = pos_x / max_x
            pos_y = pos_y / max_y
            #scale points down to prevent photos overlapping edges
            pos_x = pos_x * (1 - (size/2))
            pos_y = pos_y * (1 - (size/2))
            #convert to kivy's coordinate system
            pos_x = (pos_x + 1) / 2
            pos_y = (pos_y + 1) / 2
            #offset points to correct for photo size
            pos_x = pos_x - (size / 2)
            pos_y = pos_y - (size / 2)
            position = (collage.width * pos_x, collage.height * pos_y)

            #forces lowmem mode if more than a certain number of photos
            if len(photos) > 8:
                lowmem = True
            else:
                lowmem = False
            self.collage_ = collage
            self.fullpath_ = photo[0]
            self.position_ = position
            self.size_ = size
            self.angle_ = rand_angle
            self.lowmem_ = lowmem

            self.add_collage_image()

    def export(self):
        self.deselect_images()
        self.filechooser_popup()

    def filechooser_popup(self):
        content = FileBrowser(ok_text='Export', directory_select=False, file_editable=True, export_mode=True, file='collage.jpg')
        content.bind(on_cancel=self.dismiss_popup)
        content.bind(on_ok=self.export_check)
        self.popup = NormalPopup(title="Select File To Export To", content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def export_check(self, *_):
        path = self.popup.content.path
        file = self.popup.content.file
        self.dismiss_popup()
        if not file.lower().endswith('.jpg'):
            file = file+'.jpg'
        self.filename = os.path.join(path, file)
        if os.path.isfile(self.filename):
            app = App.get_running_app()
            content = ConfirmPopup(text='Overwrite the file "'+self.filename+'"?', yes_text='Overwrite', no_text="Cancel", warn_yes=True)
            content.bind(on_answer=self.export_overwrite_answer)
            self.popup = NormalPopup(title='Confirm Overwrite', content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4), auto_dismiss=False)
            self.popup.open()
        else:
            self.export_finish()

    def export_overwrite_answer(self, instance, answer):
        del instance
        if answer == 'yes':
            self.dismiss_popup()
            self.export_finish()

    def export_finish(self):
        app = App.get_running_app()
        content = MessagePopup(text='Exporting Collage')
        if len(self.images) > 8:
            message = 'Exporting Collage, This May Take Several Minutes, Please Wait...'
        else:
            message = 'Exporting Collage, Please Wait...'
        self.popup = NormalPopup(title=message, content=content, size_hint=(None, None), size=(app.popup_x, app.button_scale * 4))
        self.popup.open()

        #Wait a cycle so the popup can display
        Clock.schedule_once(self.export_process)

    def export_process(self, *_):
        if self.resolution == 'High':
            self.export_scale = 4
        elif self.resolution == 'Low':
            self.export_scale = 1
        else:
            self.export_scale = 2

        #wait for full sized images to load
        check_images = []
        if self.export_scale > 1:
            for image in self.images:
                async_image = image.children[0].children[0]
                if not async_image.is_full_size:
                    async_image.loadfullsize = True
                    async_image._load_fullsize()
                    check_images.append(async_image)
        while check_images:
            for image in check_images:
                if image.is_full_size:
                    check_images.remove(image)

        #wait a cycle so kivy can finish displaying the textures
        Clock.schedule_once(self.export_collage_as_image)

    def export_collage_as_image(self, *_):
        collage = self.ids['collageHolder']
        exported = self.export_scaled_jpg(collage, self.filename, image_scale=self.export_scale)
        app = App.get_running_app()
        self.dismiss_popup()
        if exported is True:
            app.message("Exported "+self.filename)
        else:
            app.message('Export error: '+exported)

    def export_scaled_jpg(self, widget, filename, image_scale=1):
        from kivy.graphics import (Translate, Fbo, ClearColor, ClearBuffers, Scale)
        re_size = (widget.width * image_scale, widget.height * image_scale)

        if widget.parent is not None:
            canvas_parent_index = widget.parent.canvas.indexof(widget.canvas)
            if canvas_parent_index > -1:
                widget.parent.canvas.remove(widget.canvas)

        try:
            fbo = Fbo(size=re_size, with_stencilbuffer=True)
            with fbo:
                ClearColor(0, 0, 0, 0)
                ClearBuffers()
                Scale(image_scale, -image_scale, image_scale)
                Translate(-widget.x, -widget.y - widget.height, 0)

            fbo.add(widget.canvas)
            fbo.draw()
            from io import BytesIO
            image_bytes = BytesIO()
            fbo.texture.save(image_bytes, flipped=False, fmt='png')
            image_bytes.seek(0)
            from PIL import Image
            image = Image.open(image_bytes)
            image = image.convert('RGB')
            image.save(filename)
            exported = True
        except Exception as ex:
            exported = str(ex)
        try:
            fbo.remove(widget.canvas)
        except:
            pass

        if widget.parent is not None and canvas_parent_index > -1:
            widget.parent.canvas.insert(canvas_parent_index, widget.canvas)
        return exported

    def change_transform(self, transform_mode):
        for container in self.images:
            if transform_mode == 'rotscale':
                container.do_rotation = True
                container.do_scale = True
                container.do_translation = False
            elif transform_mode == 'rotate':
                container.do_rotation = True
                container.do_scale = False
                container.do_translation = False
            elif transform_mode == 'scale':
                container.do_rotation = False
                container.do_scale = True
                container.do_translation = False
            else:
                container.do_rotation = True
                container.do_scale = True
                container.do_translation = True

    def on_sort_reverse(self, *_):
        """Updates the sort reverse button's state variable, since kivy doesnt just use True/False for button states."""

        app = App.get_running_app()
        self.sort_reverse_button = 'down' if to_bool(app.config.get('Sorting', 'album_sort_reverse')) else 'normal'

    def drop_widget(self, fullpath, position, dropped_type='file', aspect=1):
        """Called when a widget is dropped.  Determine photo dragged, and where it needs to go."""

        collage = self.ids['collageHolder']
        position = collage.to_widget(*position)
        self.collage_ = collage
        self.fullpath_ = fullpath
        self.position_ = position
        self.aspect = aspect
        self.add_collage_image()

    '''def add_collage_image(self, collage, fullpath, position, size=0.5, angle=0, lowmem=False, aspect=1):
        if not lowmem:
            if len(self.images) > 8:
                lowmem = True
        if collage.collide_point(*position):
            self.deselect_images()
            app = App.get_running_app()
            photoinfo = app.Photo.exist(fullpath)
            file = os.path.join(photoinfo[2], photoinfo[0])
            orientation = photoinfo[13]
            if orientation == 3 or orientation == 4:
                angle_offset = 180
            elif orientation == 5 or orientation == 6:
                angle_offset = 270
            elif orientation == 7 or orientation == 8:
                angle_offset = 90
            else:
                angle_offset = 0
            if orientation in [2, 4, 5, 7]:
                mirror = True
            else:
                mirror = False
            width = collage.width
            image_holder = ScatterImage(owner=self, source=file, rotation=angle + angle_offset, mirror=mirror, image_angle=0, photoinfo=photoinfo, lowmem=lowmem, aspect=aspect)
            image_holder.scale = size
            image_holder.selected = True
            if aspect < 1:
                image_holder.width = width * aspect
                image_holder.height = width
            else:
                image_holder.width = width
                image_holder.height = width / aspect
            self.images.append(image_holder)
            image_holder.pos = (position[0] - (width * size / 2), position[1] - (width * size / 2))
            collage.add_widget(image_holder)'''

    def show_selected(self):
        """Scrolls the treeview to the currently selected folder"""

        database = self.ids['albumContainer']
        database_interior = self.ids['album']
        selected = self.selected
        data = database.data
        current_folder = None
        for i, node in enumerate(data):
            if node['target'] == selected and node['type'] == self.type:
                current_folder = node
                break
        if current_folder is not None:
            database_interior.selected = current_folder
            database.scroll_to_selected()

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
        """Deactivates running processes if applicable.
        Returns: True if something was deactivated, False if not.
        """

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
                #normal keypresses
                pass
            elif self.popup and self.popup.open:
                if key == 'enter':
                    self.popup.content.dispatch('on_answer', 'yes')

    def scroll_photolist(self):
        """Scroll the right-side photo list to the current active photo."""

        photolist = self.ids['albumContainer']
        self.show_selected()
        photolist.scroll_to_selected()

    def refresh_all(self):
        self.refresh_photolist()
        self.refresh_photoview()

    def update_selected(self):
        pass

    def refresh_photolist(self):
        """Reloads and sorts the photo list"""

        app = App.get_running_app()

        #Get photo list
        self.photos = []
        if self.type == 'Album':
            for albuminfo in app.albums:
                if albuminfo['name'] == self.target:
                    photo_paths = albuminfo['photos']
                    for fullpath in photo_paths:
                        photoinfo = app.Photo.exist(fullpath)
                        if photoinfo:
                            self.photos.append(photoinfo)
        elif self.type == 'Tag':
            self.photos = app.Tag.photos(self.target)
        else:
            self.photos = app.Photo.by_folder(self.target)

        #Remove video files
        temp_photos = []
        for photo in self.photos:
            source = os.path.join(photo[2], photo[0])
            isvideo = os.path.splitext(source)[1].lower() in movietypes
            if not isvideo:
                temp_photos.append(photo)
        self.photos = temp_photos

        #Sort photos
        if self.sort_method == 'Imported':
            sorted_photos = sorted(self.photos, key=lambda x: x[6], reverse=self.sort_reverse)
        elif self.sort_method == 'Modified':
            sorted_photos = sorted(self.photos, key=lambda x: x[7], reverse=self.sort_reverse)
        elif self.sort_method == 'Owner':
            sorted_photos = sorted(self.photos, key=lambda x: x[11], reverse=self.sort_reverse)
        elif self.sort_method == 'Name':
            sorted_photos = sorted(self.photos, key=lambda x: os.path.basename(x[0]), reverse=self.sort_reverse)
        else:
            sorted_photos = sorted(self.photos, key=lambda x: x[0], reverse=self.sort_reverse)
        self.photos = sorted_photos

    def refresh_photoview(self):
        #refresh recycleview
        photolist = self.ids['albumContainer']
        photodatas = []
        for photo in self.photos:
            source = os.path.join(photo[2], photo[0])
            filename = os.path.basename(photo[0])
            photodata = {
                'text': filename,
                'fullpath': photo[0],
                'temporary': True,
                'photoinfo': photo,
                'folder': self.selected,
                'database_folder': photo[2],
                'filename': filename,
                'target': self.selected,
                'type': self.type,
                'owner': self,
                'video': False,
                'photo_orientation': photo[13],
                'source': source,
                'title': photo[10],
                'selected': False,
                'selectable': True,
                'dragable': True
            }
            photodatas.append(photodata)
        photolist.data = photodatas

    def clear_photolist(self):
        photolist = self.ids['albumContainer']
        photolist.data = []

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

    def on_leave(self):
        """Called when the screen is left.  Clean up some things."""

        self.clear_collage()
        self.clear_photolist()

    def on_enter(self):
        """Called when the screen is entered.  Set up variables and widgets, and prepare to view images."""

        app = App.get_running_app()

        self.ids['leftpanel'].width = app.left_panel_width()
        self.ids['moveButton'].state = 'down'
        self.ids['rotateButton'].state = 'normal'
        self.color_select = ColorDropDown(owner=self)
        self.resolution_select = ResolutionDropDown(owner=self)
        self.aspect_select = ExportAspectRatioDropDown(owner=self)
        self.add_remove = AddRemoveDropDown(owner=self)

        #import variables
        self.target = app.target
        self.type = app.type

        #set up sort buttons
        self.sort_dropdown = AlbumSortDropDown()
        self.sort_dropdown.bind(on_select=lambda instance, x: self.resort_method(x))
        self.sort_method = app.config.get('Sorting', 'album_sort')
        self.sort_reverse = to_bool(app.config.get('Sorting', 'album_sort_reverse'))

        #refresh views
        self.refresh_photolist()
        self.refresh_photoview()

