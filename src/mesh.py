from config import *
from OpenGL.GL import *

class Mesh:
    """
    Class representing a basic mesh for OpenGL rendering.

    Attributes:
    - vertex_count (int): The number of vertices in the mesh.
    - vao (int): Vertex Array Object identifier.
    - vbo (int): Vertex Buffer Object identifier.

    Methods:
    - __init__(self): Initializes the Mesh object.
    - draw(self) -> None: Draws the mesh.
    - destroy(self) -> None: Destroys the mesh, releasing associated OpenGL resources.

    Usage:
    mesh = Mesh()
    mesh.draw()
    mesh.destroy()
    """

    def __init__(self):
        """
        Initializes the Mesh object.
        """
        self.vertex_count = 0
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

    def draw(self) -> None:
        """
        Draws the mesh.
        """
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """
        Destroys the mesh, releasing associated OpenGL resources.
        """
        glDeleteBuffers(1, (self.vbo,))
        glDeleteVertexArrays(1, (self.vao,))
