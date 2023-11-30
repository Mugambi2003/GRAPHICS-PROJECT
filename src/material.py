from vector import *
from config import *

@ti.func
def reflectance(cosine, idx):
    r0 = ((1.0 - idx) / (1.0 + idx))**2
    return r0 + (1.0 - r0) * ((1.0 - cosine)**5)


@ti.func
def reflect(v, n):
    return v - 2.0 * v.dot(n) * n


@ti.func
def refract(v, n, etai_over_etat):
    cos_theta = min(-v.dot(n), 1.0)
    r_out_perp = etai_over_etat * (v + cos_theta * n)
    r_out_parallel = -ti.sqrt(abs(1.0 - r_out_perp.norm_sqr())) * n
    return r_out_perp + r_out_parallel


class _material:
    def scatter(self, in_direction, p, n):
        pass


class Lambert(_material):
    def __init__(self, color):
        self.color = color
        self.index = 0
        self.roughness = 0.0
        self.ior = 1.0

    @staticmethod
    @ti.func
    def scatter(in_direction, p, n, color):
        out_direction = n + random_in_hemisphere(n)
        attenuation = color
        return True, p, out_direction, attenuation


class Metal(_material):
    def __init__(self, color, roughness):
        self.color = color
        self.index = 1
        self.roughness = min(roughness, 1.0)
        self.ior = 1.0

    @staticmethod
    @ti.func
    def scatter(in_direction, p, n, color, roughness):
        out_direction = reflect(in_direction.normalized(),
                                n) + roughness * random_in_unit_sphere()
        attenuation = color
        reflected = out_direction.dot(n) > 0.0
        return reflected, p, out_direction, attenuation


class Dielectric(_material):
    def __init__(self, ior):
        self.color = Color(1.0, 1.0, 1.0)
        self.index = 2
        self.roughness = 0.0
        self.ior = ior

    @staticmethod
    @ti.func
    def scatter(in_direction, p, n, color, ior, front_facing):
        refraction_ratio = 1.0 / ior if front_facing else ior
        unit_dir = in_direction.normalized()
        cos_theta = min(-unit_dir.dot(n), 1.0)
        sin_theta = ti.sqrt(1.0 - cos_theta * cos_theta)

        out_direction = Vector(0.0, 0.0, 0.0)
        cannot_refract = refraction_ratio * sin_theta > 1.0
        if cannot_refract or reflectance(cos_theta,
                                         refraction_ratio) > ti.random():
            out_direction = reflect(unit_dir, n)
        else:
            out_direction = refract(unit_dir, n, refraction_ratio)
        attenuation = color

        return True, p, out_direction, attenuation


@ti.data_oriented
class Materials:
    ''' List of materials for a scene.'''
    def __init__(self, n):
        self.roughness = ti.field(ti.f32)
        self.colors = ti.Vector.field(3, dtype=ti.f32)
        self.mat_index = ti.field(ti.u32)
        self.ior = ti.field(ti.f32)
        ti.root.dense(ti.i, n).place(self.roughness, self.colors,
                                     self.mat_index, self.ior)

    def set(self, i, material):
        self.colors[i] = material.color
        self.mat_index[i] = material.index
        self.roughness[i] = material.roughness
        self.ior[i] = material.ior

    @ti.func
    def scatter(self, i, ray_direction, p, n, front_facing):
        ''' Get the scattered ray that hits a material '''
        mat_index = self.mat_index[i]
        color = self.colors[i]
        roughness = self.roughness[i]
        ior = self.ior[i]
        reflected = True
        out_origin = Point(0.0, 0.0, 0.0)
        out_direction = Vector(0.0, 0.0, 0.0)
        attenuation = Color(0.0, 0.0, 0.0)

        if mat_index == 0:
            reflected, out_origin, out_direction, attenuation = Lambert.scatter(
                ray_direction, p, n, color)
        elif mat_index == 1:
            reflected, out_origin, out_direction, attenuation = Metal.scatter(
                ray_direction, p, n, color, roughness)
        else:
            reflected, out_origin, out_direction, attenuation = Dielectric.scatter(
                ray_direction, p, n, color, ior, front_facing)
        return reflected, out_origin, out_direction, attenuation


class Material:

    def __init__(self, minDetail: int, maxDetail: int):
        self.detailLevel = 0
        size = minDetail
        self.textures: list[int] = []
        self.sizes: list[int] = []
        while size < maxDetail:
            newTexture = glGenTextures(1)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, newTexture)

            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

            glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA32F, size, size)
            self.textures.append(newTexture)
            self.sizes.append(size)
            size *= 2

    def upsize(self) -> None:
        """
            Attempt to increase detail level
        """
        self.detailLevel = min(len(self.textures) - 1, self.detailLevel + 1)

    def downsize(self) -> None:
        """
            Attempt to decrease detail level
        """
        self.detailLevel = max(0, self.detailLevel - 1)

    def writeTo(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindImageTexture(0, self.textures[self.detailLevel], 0, GL_FALSE, 0, GL_WRITE_ONLY, GL_RGBA32F)

    def readFrom(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.textures[self.detailLevel])

    def destroy(self) -> None:
        glDeleteTextures(len(self.textures), self.textures)