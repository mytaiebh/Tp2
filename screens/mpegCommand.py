import os
from typing import Any

from ffpyplayer import tools as fftools

from generalconstants import containers, video_codecs, containers_friendly, video_codecs_friendly, audio_codecs, \
    audio_codecs_friendly, containers_extensions





class MpegCommand:
    #constructeur
    def __init__(self):
        self.__input_folder = ''
        self.__input_filename = ''
        self.__output_file_folder = ''
        self.__input_size = []
        self.__noaudio = False
        self.__input_images = False
        self.__input_file = None
        self.__input_framerate = None
        self.__input_pixel_format = None
        self.__encoding_settings = None
        self.__start = None
        self.__duration = None


    #les setters
    def set_input_folder(self, input_folder):
        self.__input_folder = input_folder

    def set_input_filename(self, input_filename):
        self.__input_filename = input_filename

    def set_output_file_folder(self, output_file_folder):
        self.__output_file_folder = output_file_folder


    def set_input_size(self, input_size):
        self.__input_size = input_size

    def set_noaudio(self, noaudio):
        self.__noaudio = noaudio

    def set_input_images(self, input_images):
        self.__input_images = input_images

    def set_input_file(self, input_file):
        self.__input_file = input_file
    def set_input_framerate(self, input_framerate):
        self.__input_framerate = input_framerate

    def set_input_pixel_format(self, input_pixel_format):
        self.__input_pixel_format = input_pixel_format

    def set_encoding_settings(self, encoding_settings):
        self.__encoding_settings = encoding_settings

    def set_start(self, start):
        self.__start = start

    def set_duration(self,duration):
        self.__duration = duration

    #fonction ffmpeg_command

    def ffmpeg_command(self):
        if not self.__encoding_settings:
            encoding_settings = self.__encoding_settings
        if encoding_settings['file_format'].lower() == 'auto':
            file_format = 'MP4'
            pixels_number = self.__input_size[0] * self.__input_size[1]
            video_bitrate = str(pixels_number / 250)
            video_codec = 'libx264'
            audio_codec = 'aac'
            audio_bitrate = '192'
            encoding_speed = 'fast'
            deinterlace = False
            resize = False
            resize_width = self.__input_size[0]
            resize_height = self.__input_size[1]
            encoding_command = ''
            extension = 'mp4'
        else:
            file_format = containers[containers_friendly.index(encoding_settings['file_format'])]
            video_codec = video_codecs[video_codecs_friendly.index(encoding_settings['video_codec'])]
            audio_codec = audio_codecs[audio_codecs_friendly.index(encoding_settings['audio_codec'])]
            video_bitrate = encoding_settings['video_bitrate']
            audio_bitrate = encoding_settings['audio_bitrate']
            encoding_speed = encoding_settings['encoding_speed'].lower()
            deinterlace = encoding_settings['deinterlace']
            resize = encoding_settings['resize']
            resize_width = encoding_settings['width']
            resize_height = encoding_settings['height']
            encoding_command = encoding_settings['command_line']
            extension = containers_extensions[containers.index(file_format)]

        if self.__start is not None:
            seek = ' -ss '+str(self.__start)
        else:
            seek = ''
        if self.__duration is not None:
            duration = ' -t '+str(self.__duration)
        else:
            duration = ''
        if not self.__input_file:
            input_file = self.__input_folder+os.path.sep+self.__input_filename
        if self.__input_framerate:
            output_framerate = self.new_framerate(video_codec, self.__input_framerate)
        else:
            output_framerate = False
        if output_framerate:
            framerate_setting = "-r "+str(output_framerate[0] / output_framerate[1])
        else:
            framerate_setting = ""
        if self.__input_images:
            input_format_settings = '-f image2pipe -vcodec mjpeg ' + framerate_setting
        else:
            self.input_format_settings = ''
        if self.__input_pixel_format:
            output_pixel_format = self.new_pixel_format(video_codec, self.__input_pixel_format)
        else:
            output_pixel_format = False
        if output_pixel_format:
            pixel_format_setting = "-pix_fmt "+str(output_pixel_format)
        else:
            pixel_format_setting = ""

        if video_codec == 'libx264':
            speed_setting = "-preset "+encoding_speed
        else:
            speed_setting = ''

        video_bitrate_settings = "-b:v "+video_bitrate+"k"
        if not self.__noaudio:
            audio_bitrate_settings = "-b:a "+audio_bitrate+"k"
            audio_codec_settings = "-c:a " + audio_codec + " -strict -2"
        else:
            audio_bitrate_settings = ''
            audio_codec_settings = ''
        video_codec_settings = "-c:v "+video_codec
        file_format_settings = "-f "+file_format

        if resize and (self.__input_size[0] > int(resize_width) or self.__input_size[1] > int(resize_height)):
            resize_settings = 'scale='+resize_width+":"+resize_height
        else:
            resize_settings = ''
        if deinterlace:
            deinterlace_settings = "yadif"
        else:
            deinterlace_settings = ""
        if deinterlace_settings or resize_settings:
            filter_settings = ' -vf "'
            if deinterlace_settings:
                filter_settings = filter_settings+deinterlace_settings
                if resize_settings:
                    filter_settings = filter_settings+', '+resize_settings
            else:
                filter_settings = filter_settings+resize_settings
            filter_settings = filter_settings+'" '
        else:
            filter_settings = ""

        if encoding_command:
            #check if encoding command is valid

            if '%i' not in encoding_command:
                return [False, 'Input file must be specified', '']
            if '%c' not in encoding_command:
                extension = ''
                if '-f' in encoding_command:
                    detect_format = encoding_command[encoding_command.find('-f')+2:].strip().split(' ')[0].lower()
                    supported_formats = fftools.get_fmts(output=True)
                    if detect_format in supported_formats[0]:
                        format_index = supported_formats[0].index(detect_format)
                        extension_list = supported_formats[2][format_index]
                        if extension_list:
                            extension = extension_list[0]
                if not extension:
                    return [False, 'Could not determine ffmpeg container format.', '']
            output_filename = os.path.splitext(self.__input_filename)[0]+'.'+extension
            output_file = self.__output_file_folder+os.path.sep+output_filename
            input_settings = ' -i "'+input_file+'" '
            encoding_command_reformat = encoding_command.replace('%c', file_format_settings).replace('%v', video_codec_settings).replace('%a', audio_codec_settings).replace('%f', framerate_setting).replace('%p', pixel_format_setting).replace('%b', video_bitrate_settings).replace('%d', audio_bitrate_settings).replace('%i', input_settings).replace('%%', '%')
            command = 'ffmpeg'+seek+' '+input_format_settings+encoding_command_reformat+duration+' "'+output_file+'"'
        else:
            output_filename = os.path.splitext(self.__input_filename)[0]+'.'+extension
            output_file = self.__output_file_folder+os.path.sep+output_filename
            #command = 'ffmpeg '+file_format_settings+' -i "'+input_file+'"'+filter_settings+' -sn '+speed_setting+' '+video_codec_settings+' '+audio_codec_settings+' '+framerate_setting+' '+pixel_format_setting+' '+video_bitrate_settings+' '+audio_bitrate_settings+' "'+output_file+'"'
            command = 'ffmpeg'+seek+' '+input_format_settings+' -i "'+input_file+'" '+file_format_settings+' '+filter_settings+' -sn '+speed_setting+' '+video_codec_settings+' '+audio_codec_settings+' '+framerate_setting+' '+pixel_format_setting+' '+video_bitrate_settings+' '+audio_bitrate_settings+duration+' "'+output_file+'"'
        return [True, command, output_filename]

    def new_pixel_format(self, codec, pixel_format):
        """Given the old pixel format, determine what the closest supported format for the current video codec is.
        Argument:
            pixel_format: String, a pixel format name
        Returns: String, a pixel format name, or False if none found.
        """

        available_pixel_formats = fftools.get_supported_pixfmts(codec_name=codec, pix_fmt=pixel_format)
        if available_pixel_formats:
            return available_pixel_formats[0]
        else:
            return False

    def new_framerate(self, codec, framerate):
        """Given the old framerate, determine what the closest supported framerate for the current video codec is.
        Argument:
            framerate: 2-Tuple, frame rate numerator, and denominator
        Returns: 2-Tuple, frame rate numerator, and denominator
        """

        framerates = fftools.get_supported_framerates(codec_name=codec, rate=framerate)
        if framerates:
            return framerates[0]
        else:
            #all framerates supported, just return the given one
            return framerate
