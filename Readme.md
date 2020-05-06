# Snu Photo Manager

## Initial setup
alembic upgrade head # to create the database
cd ~/.snuphotomanager # to go in database directory



A feature-rich photo manager and editor written in python and using the Kivy library.  
It should run on any platform that the required libraries can be run on.  So far, I have made Windows, Linux (Ubuntu 16+) and Android binaries.  It should be possible to create OSX and ios binaries as well, but I do not have the required hardware to do so.  
Download latest binaries at: www.snuq.com/snuphotomanager/  
Note that the android version is very beta - some features are missing, it is pretty slow, and it is not yet a signed executable (debug only for now).  


Watch the demo video:

[![Demo Video](https://img.youtube.com/vi/1Bgc5UyPOS4/0.jpg)](https://www.youtube.com/watch?v=1Bgc5UyPOS4)


## Some features that are implemented:  
* Photo and video database with folders, albums, tags and favorites.  
* Multiple database support (folders), ability to transfer between databases (for archival purposes).  
* Importing from multiple sources at once.  
* Drag-n-drop organization.  
* Touch-friendly interface.  
* Simple and advanced color editing: brightness, contrast, saturation, gamma, color curves, tinting.  
* Simple and advanced filters: sharpen, soften, vignette, edge blur.  
* Noise reduction: Despeckle, edge-preserve blur, non-local means denoise.  
* Image edits: rotate (and straighten), crop, image border overlays (frames).  
* All editing features apply to videos as well.  
* Video conversions (reencoding using presets).  
* Collage creation from any number of photos.
* Exporting with watermarks and resizing, export to a folder or FTP.  


## Installation:  
Depending on your browser, left clicking the files may not download them, you may need to right click on the file and select save as, or save link as.  


### Windows:  
* Download the "Snu Photo Manager Installer v#.#.###.exe" file.  
* Run the file.  


### Linux:  
Due to many differences in linux desktop environments, the install script may not work.  If this is the case, you will need to extract the .tar.gz file and create a shortcut yourself.  
* Download both files in the 'linux' subdirectory.  
* Place the files in the location where you would like the 'Snu Photo Manager' folder to be (such as in your home directory).  
* Run the 'snuphotomanagerinstall' file.  Double clicking may work, otherwise open a terminal, go to the directory, and type "./snuphotomanagerinstall" (without the quotes).
* A new shortcut file should be created in the current folder: 'Snu Photo Manager.desktop', this may be moved to your desktop or any other location.  


### Android:  
For now, side-loading of apps is required to be enabled.  Depending on your device, this may be enabled already, or may be impossible to enable.  
* Download "snuphotomanager-#.#.###-debug.apk" to your android device, or transfer from a computer using your preferred method.  
* Run the file from your file manager of choice.  


### Manual Installation:  
* Install Python 3, tested with 3.4.4, 3.5.2 and 3.7.3.  
* Install the Python packages:  
   * Kivy (Tested with 1.10.0 and 1.11.0)  
   * ffpyplayer (Tested with 4.0.1 and 4.2.0)  
   * Pillow (Tested with 3.1.2, 4.1.1 and 6.0.0)  
   * numpy (Tested with 1.12.1, 1.13.3 and 1.16.3) (not strictly required, but some features will be missing without it).  
   * opencv-python (Tested with 3.2.0.7, 3.3.0.10 and 4.1.0.25) (same as numpy).  
* Download the repository.  
* Unzip the repository to the location of your choice.  
* For video conversions, the ffmpeg executable must be installed in a path that Python can find (the root directory of Snu Photo Manager will work).  Tested with 2.8.11.  
* Run "main.py".