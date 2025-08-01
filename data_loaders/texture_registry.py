import json

from typing_extensions import Self

from data_loaders.terminal_texture import TerminalTexture


class TextureRegistry:
    _instance = None
    _initialized = False

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._textures: dict[str, TerminalTexture] = {}
        self._loaded = False
        TextureRegistry._initialized = True

    def load(self, path: str) -> None:
        try:
            with open(path) as file:
                texture_data = json.load(file)

            for name, data in texture_data.items():
                self._textures[name] = TerminalTexture(data["graphics"], data["size"])
            self._loaded = True

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Texture file not found: {path}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON in texture file: {path}: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error loading texture file: {path}: {e}") from e

    def __getitem__(self, texture_name: str) -> TerminalTexture:
        if not self._loaded:
            raise RuntimeError("Textures not loaded. Call load_from_file() first.")

        if texture_name not in self._textures:
            raise KeyError(
                f"Texture '{texture_name}' not found. Available textures: {list(self._textures.keys())}"
            )

        return self._textures[texture_name]

    def __contains__(self, texture_name: str) -> bool:
        return texture_name in self._textures

    def list_textures(self) -> list[str]:
        return list(self._textures.keys())
