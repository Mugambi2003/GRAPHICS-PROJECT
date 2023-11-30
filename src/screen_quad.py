# Import necessary modules and classes
from config import *
import mesh

class ScreenQuad(mesh.Mesh):
    """
    Represents a screen quad mesh, inheriting from the Mesh class.
    """

    def __init__(self):
        """
        Initialize the ScreenQuad object.
        """

        # Call the constructor of the parent Mesh class
        super().__init__()

        # Define vertices for a screen quad
        vertices = np.array(
            (1.0,  1.0,  # top-right
            -1.0,  1.0,  # top-left
            -1.0, -1.0,  # bottom-left
            -1.0, -1.0,  # bottom-left
             1.0, -1.0,  # bottom-right
             1.0,  1.0),  # top-right
             dtype=np.float32
        )

        # Set the vertex count for the screen quad
        self.vertex_count = 6

        # Buffer the vertex data to the GPU
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Enable vertex attribute array and specify its layout
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))
