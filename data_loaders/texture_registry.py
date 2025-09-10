import json
from collections.abc import Sequence

from typing_extensions import Self

if __name__ == "__main__":
    import sys
    from os.path import abspath, dirname

    sys.path.append(dirname(dirname(abspath(__file__))))

from data_loaders.terminal_texture import Texture

_TERMINAL_GRAPHICS_PATH = "graphic_data/graphics.json"


class TextureRegistry(Sequence):
    _instance = None
    _initialized = False

    def __new__(cls, _) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, path: str) -> None:
        self._textures: dict[str, Texture] = {}

        self._load(path)

        TextureRegistry._initialized = True

    def _load(self, path: str = None) -> None:
        try:
            if path is None:
                path = _TERMINAL_GRAPHICS_PATH
            with open(path) as file:
                texture_data = json.load(file)

            for name, data in texture_data.items():
                self._textures[name] = Texture(name, data["graphics"], data["color"], data["bold"], tuple(data["size"]))

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Texture file not found: {path}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON in texture file: {path}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error loading texture file: {path}: {e}") from e

    def clear_data(self):
        self._textures.clear()

    def __getitem__(self, texture_name: str) -> Texture:
        if not TextureRegistry._initialized:
            raise RuntimeError("Textures not loaded. Initialize the registry")

        if texture_name not in self._textures:
            raise KeyError(f"Texture '{texture_name}' not found. Available textures: {list(self._textures.keys())}")

        return self._textures[texture_name]

    def __contains__(self, texture_name: str) -> bool:
        return texture_name in self._textures

    def __len__(self) -> int:
        return len(self._textures)

    def list_textures(self) -> list[str]:
        return list(self._textures.keys())

    @classmethod
    def register(cls, texture: Texture) -> None:
        if texture.name in cls.instance()._textures:
            raise ValueError(f"Texture '{texture.name}' already exists in the registry.")
        cls.instance()._textures[texture.name] = texture

    @classmethod
    def from_dict(cls, data):
        _tex_name = data.get("name", None)
        _tex_size = data.get("size", None)

        if _tex_name:
            tex = cls.instance()[_tex_name]
        else:
            raise ValueError("Texture name is required to load from dict")

        if _tex_size and tex.size != tuple(_tex_size):
            raise ValueError("error with loaded texture size")

        return tex

    @classmethod
    def instance(cls):
        if cls._instance is None:
            raise RuntimeError("Textures not loaded. Initialize the registry")
        return cls._instance


def load_textures():
    _ = TextureRegistry(_TERMINAL_GRAPHICS_PATH)

def change_graphics_path(new_path: str):
    global _TERMINAL_GRAPHICS_PATH
    _TERMINAL_GRAPHICS_PATH = new_path


if __name__ == "__main__":
    load_textures()

    registry2 = TextureRegistry.instance()
    print("Available textures:", registry2.list_textures())

    dot1 = registry2["dot"]
    print(list(dot1))
