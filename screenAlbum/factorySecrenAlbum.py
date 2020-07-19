from screenAlbum.EditColorImageAdvanced import EditColorImageAdvanced
from screenAlbum.EditConvertImage import EditConvertImage
from screenAlbum.EditConvertVideo import EditConvertVideo
from screenAlbum.EditCropImage import EditCropImage
from screenAlbum.EditDenoiseImage import EditDenoiseImage
from screenAlbum.EditFilterImage import EditFilterImage
from screenAlbum.EditMain import EditMain
from screenAlbum.EditNone import EditNone
from screenAlbum.EditRotateImage import EditRotateImage
from screenAlbum.PhotoViewer import PhotoViewer
from screenAlbum.RemoveFromTagButton import RemoveFromTagButton
from screenAlbum.RemoveTagButton import RemoveTagButton
from screenAlbum.TagSelectButton import TagSelectButton
from screenAlbum.VideoViewer import VideoViewer
from screenAlbum.editBorderImage import EditBorderImage
from screenAlbum.editColorImage import EditColorImage
from screenAlbum.treeViewInfo import TreeViewInfo

class FactoryScreenAlbum():
    def makeTreeViewInfo(self, title):
        return TreeViewInfo(title=title)
    def makeEditColorImage(self,owner):
        return EditColorImage(owner=owner)
    def makeEditBorderImage(self,owner):
        return EditBorderImage(owner=owner)
    def makeVideoViewer(self,favorite, angle, mirror, file,photoinfo):
        return VideoViewer(favorite = favorite, angle = angle,
                           mirror = mirror, file = file, photoinfo = photoinfo)
    def makeTagSelectButton(self, type,text,target,owner):
        return TagSelectButton(type= type, text=text, target= target, owner=owner)
    def makeRemoveTagButton(self,to_remove,owner):
        return RemoveTagButton(to_remove=to_remove, owner=owner)
    def makeRemoveFromTagButton(self,to_remove,remove_from, owner):
        return RemoveFromTagButton(to_remove=to_remove,
                                   remove_from=remove_from, owner=owner)
    def makePhotoViewer(self,favorite,angle,mirror,photo_id,file,photoinfo):
        return PhotoViewer(favorite=favorite,
                           angle=angle, mirror=mirror,
                           photo_id=photo_id,
                           file=file,photoinfo=photoinfo)
    def makeEditRotateImage(self,owner):
        return EditRotateImage(owner=owner)
    def makeEditNone(self,owner):
        return EditNone(owner=owner)
    def makeEditMain(self,owner):
        return EditMain(owner=owner)
    def makeEditFilterImage(self,owner):
        return EditFilterImage(owner=owner)
    def makeEditDenoiseImage(self,owner,imagefile,image_x,image_y):
        return EditDenoiseImage(owner=owner, imagefile=imagefile, image_x=image_x,
                                image_y=image_y)
    def makeEditCropImage(self,owner,image_x, image_y):
        return EditCropImage(owner=owner,image_x=image_x, image_y=image_y)
    def makeEditConvertVideo(self,owner):
        return EditConvertVideo(owner=owner)
    def makeEditConvertImage(self,owner):
        return EditConvertImage(owner=owner)
    def makeEditColorImageAdvanced(self,owner):
        return EditColorImageAdvanced(owner=owner)
#class FactoryScreenAlbumInterface(FactoryScreenAlbumInterface):







