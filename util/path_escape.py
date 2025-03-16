import os
import sys


class PathUtil:
    @staticmethod
    def normalize_path(path):
        return os.path.normpath(path)

    @staticmethod
    def get_filesystem_encoding():
        return sys.getfilesystemencoding()

    @staticmethod
    def encode_decode_path(path):
        fs_encoding = PathUtil.get_filesystem_encoding()
        encoded_path = path.encode(fs_encoding)
        return encoded_path.decode(fs_encoding)

    @staticmethod
    def handle_path(path):
        normalized_path = PathUtil.normalize_path(path)
        return PathUtil.encode_decode_path(normalized_path)
