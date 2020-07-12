import os

from kivy.app import App
from kivy.properties import NumericProperty

from screenCollage.ScatterImage import ScatterImage


class ImageCollage:

    images = []
    collage_ = ""
    fullpath_ = None
    position_ = None
    size_ = 0.5
    angle_ = 0
    lowmem_= False
    aspect = NumericProperty(1.3333)



    def add_collage_image(self):
        if not self.lowmem:
            if len(self.images) > 8:
                lowmem = True
        if self.collage.collide_point(*self.position):
            self.deselect_images()
            app = App.get_running_app()
            photoinfo = app.Photo.exist(self.fullpath)
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
            width = self.collage.width
            image_holder = ScatterImage(owner=self, source=file, rotation=self.angle + angle_offset, mirror=mirror,
                                        image_angle=0, photoinfo=photoinfo, lowmem=lowmem, aspect=self.aspect)
            image_holder.scale = self.size
            image_holder.selected = True
            if self.aspect < 1:
                image_holder.width = width * self.aspect
                image_holder.height = width
            else:
                image_holder.width = width
                image_holder.height = width / self.aspect
            self.images.append(image_holder)
            image_holder.pos = (self.position[0] - (width * self.size / 2), self.position[1] - (width * self.size / 2))
            self.collage.add_widget(image_holder)

        def deselect_images(self):
            collage = self.ids['collageHolder']
            for image in collage.children:
                image.selected = False