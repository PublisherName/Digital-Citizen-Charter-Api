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


def download_image_from_url(url, filename):
    from io import BytesIO

    import requests
    from django.core.exceptions import ValidationError
    from django.core.files import File
    from PIL import Image

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as e:
        raise ValidationError(f"Error occurred while trying to download the image: {str(e)}")

    if response.status_code != 200:
        raise ValidationError(
            f"Unable to download image, server responded with status code: {response.status_code}"
        )

    try:
        image = Image.open(BytesIO(response.content))
    except OSError as e:
        raise ValidationError(f"Error occurred while trying to open the image: {str(e)}")

    image_io = BytesIO()
    image.save(image_io, format="JPEG")
    image_file = File(image_io, name=filename)
    return image_file
