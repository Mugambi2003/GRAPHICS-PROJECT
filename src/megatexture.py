from config import *
from PIL import Image
from OpenGL.GL import *

class MegaTexture:
    """
    Class representing a mega texture composed of multiple texture layers.

    Attributes:
    - filenames (list): List of filenames for texture layers.

    Methods:
    - __init__(self, filenames): Initializes the MegaTexture object.
    - destroy(self): Deletes the OpenGL texture.

    Usage:
    filenames = ["texture1", "texture2", ...]
    mega_texture = MegaTexture(filenames)
    mega_texture.destroy()
    """

    def __init__(self, filenames):
        """
        Initializes the MegaTexture object.

        Parameters:
        - filenames (list): List of filenames for texture layers.
        """
        texture_size = 1024
        texture_count = len(filenames)
        width = 5 * texture_size
        height = texture_size

        # Image types to include in the mega texture
        #  "albedo", "emissive", "glossiness", "normal"

        image_types = ("albedo", "emissive", "glossiness", "normal")

        # Create a list of Image objects for each texture layer
        texture_layers = [Image.new(mode="RGBA", size=(width, height)) for _ in range(texture_count)]

        # Paste individual texture images into the texture layers
        for i in range(texture_count):
            for j, image_type in enumerate(image_types):
                with Image.open(f"src/textures/{filenames[i]}/{filenames[i]}_{image_type}.png", mode="r") as img:
                    img.convert("RGBA")
                    texture_layers[i].paste(img, (j * texture_size, 0))

        # Generate and configure the OpenGL texture
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D_ARRAY, self.texture)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA32F, width, height, texture_count)

        # Upload texture layer data to OpenGL texture
        for i in range(texture_count):
            img_data = bytes(texture_layers[i].tobytes())
            glTexSubImage3D(GL_TEXTURE_2D_ARRAY, 0, 0, 0, i, width, height, 1, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    def destroy(self):
        """
        Deletes the OpenGL texture.
        """
        glDeleteTextures(1, self.texture)
