from dropDowns.AlbumSortDropDown import AlbumSortDropDown
from labels.NormalLabel import NormalLabel
from labels.ShortLabel import ShortLabel
from popups.ConfirmPopup import ConfirmPopup
from popups.NormalPopup import NormalPopup
from popups.ScanningPopup import ScanningPopup


class FactoryGeneralElements:
    def makeAlbumSortDropDown(self,):
        return AlbumSortDropDown()
    def makeConfirmPopup(self,text,yes_text,no_text,warn_yes):
        return ConfirmPopup(text=text, yes_text=yes_text, no_text=no_text, warn_yes=warn_yes)
    def makeNormalLabel(self, text,size_hint_x):
        return NormalLabel(text=text, size_hint_x=size_hint_x)
    def makeNormalPopup(self,title,content,size_hint,size,auto_dismiss):
        return NormalPopup(title=title, content=content, size_hint=size_hint,
                           size=size, auto_dismiss=auto_dismiss)
    def makeScanningPopup(self,title,auto_dismiss,size_hint,size):
        return ScanningPopup(title=title, auto_dismiss=auto_dismiss, size_hint=size_hint, size=size)
    def makeShortLabel(self):
        return ShortLabel()