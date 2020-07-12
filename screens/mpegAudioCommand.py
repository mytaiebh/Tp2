import os

from generalconstants import containers, containers_friendly, audio_codecs, audio_codecs_friendly, containers_extensions
from screens.screenAlbum import ScreenAlbum


class MpegAudioCommand:
    def __init__(self):
        self.__video_input_folder = None
        self.__video_input_filename = None
        self.__audio_input_folder  = None
        self.__audio_input_filename = None
        self.__output_file_folder = None
        self.__encoding_settings = None
        self.__start = None

    def set_video_input_folder(self, video_input_folder):
        self.__video_input_folder = video_input_folder

    def set_video_input_filename(self, video_input_filename):
        self.__video_input_filename = video_input_filename

    def set_audio_input_folder(self, audio_input_folder):
        self.__audio_input_folder = audio_input_folder

    def set_audio_input_filename(self, audio_input_filename):
        self.__audio_input_filename = audio_input_filename

    def set_output_file_folder(self, output_file_folder):
        self.__output_file_folder = output_file_folder

    def set_encoding_settings(self, encoding_settings):
        self.__encoding_settings = encoding_settings

    def set_start(self, start):
        self.__start = start

    def mpeg_audio_command(self):
        if not self.__encoding_settings:
            self.__encoding_settings = ScreenAlbum.encoding_settings
        if self.__encoding_settings['file_format'].lower() == 'auto':
            audio_codec = 'aac'
            audio_bitrate = '192'
            extension = 'mp4'
        else:
            file_format = containers[containers_friendly.index(self.__encoding_settings['file_format'])]
            audio_codec = audio_codecs[audio_codecs_friendly.index(self.__encoding_settings['audio_codec'])]
            audio_bitrate = self.__encoding_settings['audio_bitrate']
            extension = containers_extensions[containers.index(file_format)]

        if self.__start is not None:
            seek = ' -ss ' + str(self.__start)
        else:
            seek = ''
        video_file = self.__video_input_folder + os.path.sep + self.__video_input_filename
        audio_file = self.__audio_input_folder + os.path.sep + self.__audio_input_filename
        output_filename = os.path.splitext(self.__video_input_filename)[0] + '-mux.' + extension
        output_file = self.__output_file_folder + os.path.sep + output_filename
        audio_bitrate_settings = "-b:a " + audio_bitrate + "k"
        audio_codec_settings = "-c:a " + audio_codec + " -strict -2"

        command = 'ffmpeg -i "' + video_file + '"' + seek + ' -i "' + audio_file + '" -map 0:v -map 1:a -codec copy ' + audio_codec_settings + ' ' + audio_bitrate_settings + ' -shortest "' + output_file + '"'
        return [True, command, output_filename]