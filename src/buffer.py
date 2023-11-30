# Import necessary modules and classes
from config import *
import sphere
import plane
import light


class Buffer:
    """
    Represents a buffer used for storing data related to spheres, planes, and lights
    in a graphics application using OpenGL's Shader Storage Buffer Objects (SSBOs).
    """

    def __init__(self, size: int, binding: int, floatCount: int):
        """
        Initialize a Buffer object.

        Parameters:
            size (int): Size of the buffer.
            binding (int): Binding point for the buffer.
            floatCount (int): Number of float components per element in the buffer.
        """

        # Initialize buffer properties
        self.size = size
        self.binding = binding
        self.floatCount = floatCount

        # Create host and device memory for the buffer
        self.hostMemory = np.zeros(floatCount * size, dtype=np.float32)
        self.deviceMemory = glGenBuffers(1)

        # Set up OpenGL buffer storage
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.deviceMemory)
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, self.hostMemory.nbytes,
            self.hostMemory, GL_DYNAMIC_STORAGE_BIT)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, self.deviceMemory)

        # Initialize counter for updated elements
        self.elements_updated = 0

    def recordSphere(self, i: int, _sphere: sphere.Sphere) -> None:
        """
        Record the given sphere in position i. If this exceeds the buffer size,
        the sphere is not recorded.

        Parameters:
            i (int): Index in the buffer.
            _sphere (sphere.Sphere): Sphere object to be recorded.
        """

        if i >= self.size:
            return

        baseIndex = self.floatCount * i

        # Record sphere data in host memory
        self.hostMemory[baseIndex: baseIndex + 3] = _sphere.center[:]
        self.hostMemory[baseIndex + 3] = _sphere.radius
        self.hostMemory[baseIndex + 4: baseIndex + 7] = _sphere.color[:]
        self.hostMemory[baseIndex + 7] = _sphere.roughness

        # Update the counter for updated elements
        self.elements_updated += 1

    def recordPlane(self, i: int, _plane: plane.Plane) -> None:
        """
        Record the given plane in position i. If this exceeds the buffer size,
        the plane is not recorded.

        Parameters:
            i (int): Index in the buffer.
            _plane (plane.Plane): Plane object to be recorded.
        """

        if i >= self.size:
            return

        baseIndex = self.floatCount * i

        # Record plane data in host memory
        # plane: (cx cy cz umin) (tx ty tz umax) (bx by bz vmin) (nx ny nz vmax) (r g b -)
        self.hostMemory[baseIndex: baseIndex + 3] = _plane.center[:]
        self.hostMemory[baseIndex + 3] = _plane.uMin
        self.hostMemory[baseIndex + 4: baseIndex + 7] = _plane.tangent[:]
        self.hostMemory[baseIndex + 7] = _plane.uMax
        self.hostMemory[baseIndex + 8: baseIndex + 11] = _plane.bitangent[:]
        self.hostMemory[baseIndex + 11] = _plane.vMin
        self.hostMemory[baseIndex + 12: baseIndex + 15] = _plane.normal[:]
        self.hostMemory[baseIndex + 15] = _plane.vMax
        self.hostMemory[baseIndex + 16] = _plane.material_index

        # Update the counter for updated elements
        self.elements_updated += 1

    def recordLight(self, i: int, _light: light.Light) -> None:
        """
        Record the given light in position i. If this exceeds the buffer size,
        the light is not recorded.

        Parameters:
            i (int): Index in the buffer.
            _light (light.Light): Light object to be recorded.
        """

        if i >= self.size:
            return

        baseIndex = self.floatCount * i

        # Record light data in host memory
        # light: (x y z s) (r g b -)
        self.hostMemory[baseIndex: baseIndex + 3] = _light.position[:]
        self.hostMemory[baseIndex + 3] = _light.strength
        self.hostMemory[baseIndex + 4: baseIndex + 7] = _light.color[:]

        # Update the counter for updated elements
        self.elements_updated += 1

    def readFrom(self) -> None:
        """
        Upload the CPU data to the buffer, then arm it for reading.
        """

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.deviceMemory)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.floatCount * 4 * self.elements_updated, self.hostMemory)
        glBindBufferBase
