# Trait artwork

`source/` contains the 28 approved transparent PNG masters. The Akakiru icon uses a katana with a straight hilt. `preview.png` shows the complete set at the game's native 120-pixel size.

Runtime DDS files are in `AuraClash/gfx/interface/icons/traits/`. They retain the original filenames and use 120 × 120 uncompressed BGRA textures with alpha and no mipmaps.

Rebuild with Python and Pillow:

```sh
python tools/build_trait_icons.py
python tools/build_trait_icons.py --check
```

The artwork is Aura Clash Setting Content under [LICENSE-CONTENT.md](../../LICENSE-CONTENT.md).
