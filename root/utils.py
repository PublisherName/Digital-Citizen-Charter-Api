""" This file contains the utility functions for the project. """

import os
import hashlib
from django.utils.deconstruct import deconstructible
from django.core.exceptions import SuspiciousFileOperation


@deconstructible
class UploadToPathAndRename:  # pylint: disable=too-few-public-methods
    """This class is used to rename the uploaded file to a unique name."""

    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):

        if os.path.isabs(filename) or filename.startswith(".."):
            raise SuspiciousFileOperation(f"Invalid filename: {filename}")

        extension = os.path.splitext(filename)[1]
        filename = hashlib.md5(filename.encode()).hexdigest()
        return os.path.join(self.path, filename + extension)
