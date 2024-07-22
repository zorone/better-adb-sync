from typing import Iterable, Tuple, NoReturn
import os
import subprocess

from ..SAOLogging import logging_fatal

from .Base import FileSystem

class LocalFileSystem(FileSystem):
    @property
    def sep(self) -> str:
        return os.path.sep

    def unlink(self, path: str) -> None:
        os.unlink(path)

    def rmdir(self, path: str) -> None:
        os.rmdir(path)

    def makedirs(self, path: str) -> None:
        os.makedirs(path, exist_ok = True)

    def realpath(self, path: str) -> str:
        return os.path.realpath(path)

    def lstat(self, path: str) -> os.stat_result:
        return os.lstat(path)

    def lstat_in_dir(self, path: str) -> Iterable[Tuple[str, os.stat_result]]:
        for filename in os.listdir(path):
            yield filename, self.lstat(self.join(path, filename))

    def utime(self, path: str, times: Tuple[int, int]) -> None:
        os.utime(path, times)

    def join(self, base: str, leaf: str) -> str:
        return os.path.join(base, leaf)

    def split(self, path: str) -> Tuple[str, str]:
        return os.path.split(path)

    def normpath(self, path: str) -> str:
        path = os.path.normpath(path)
        return self.convert_invalid_file_name(path)

    def push_file_here(self, source: str, destination: str, show_progress: bool = False) -> None:
        if show_progress:
            kwargs_call = {}
        else:
            kwargs_call = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL
            }
        if subprocess.call(self.adb_arguments + ["pull", source, destination], **kwargs_call):
            logging_fatal("Non-zero exit code from adb pull")

    def setup_invalid_name_check(self) -> NoReturn:
        self.set_invalid_name_potential()
        self.convert_table = str.maketrans('\/*:?"<>|', '_________')

    def set_invalid_name_potential(self) -> NoReturn:
        self.has_invalid_name_potential = os.name == 'nt'

    def convert_invalid_file_name(self, path_destination: str) -> str: # usually has this problem on Windows
        # TODO implement flag for accepting dictionary of invalid-replacement pairs
        # (or single character replacement if provide a character instead)
        # TODO implement flag for accepting a list of invalid characters
        # TODO make character map customizable
        # TODO implement different list of invalid character for each file system
        if self.has_invalid_name_potential:
            return path_destination.translate(self.convert_table)
        else:
            return path_destination
