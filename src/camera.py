# Import necessary modules and classes
from config import *


class Camera:
    """
    Represents a camera in the scene
    """

    def __init__(self, position: list[float]):
        """
        Create a new camera at the given position facing in the given direction.

        Parameters:
            position (array [3,1]): The initial position of the camera.
        """

        # Initialize camera properties
        self.position = np.array(position, dtype=np.float32)
        self.theta = 0
        self.phi = 0

        # Recalculate camera vectors based on initial angles
        self.recalculateVectors()

    def recalculateVectors(self) -> None:
        """
        Calculate the camera's fundamental vectors.
        """

        # Calculate forward vector based on spherical coordinates
        self.forwards = np.array(
            [
                np.cos(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.phi))
            ], dtype=np.float32
        )

        # Calculate the right vector using cross product
        self.right = pyrr.vector.normalize(
            pyrr.vector3.cross(self.forwards, np.array([0, 0, 1], dtype=np.float32))
        )

        # Calculate the up vector using cross product
        self.up = pyrr.vector.normalize(
            pyrr.vector3.cross(self.right, self.forwards)
        )
