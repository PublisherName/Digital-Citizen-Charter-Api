"""This file contains the utility functions for the project."""

import hashlib
import os

from django.core.exceptions import SuspiciousFileOperation
from django.utils.deconstruct import deconstructible


@deconstructible
class UploadToPathAndRename:
    """This class is used to rename the uploaded file to a unique name."""

    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        if os.path.isabs(filename) or filename.startswith(".."):
            raise SuspiciousFileOperation(f"Invalid filename: {filename}")

        extension = os.path.splitext(filename)[1]
        filename = hashlib.sha256(filename.encode()).hexdigest()
        return os.path.join(self.path, filename + extension)
