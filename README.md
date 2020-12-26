# channelpack

A small tool for [channel packing](http://wiki.polycount.com/wiki/ChannelPacking).

This is currently a work-in-progress, but can be demoed with `python channelpack.py example/map.txt` to combine
`examples/map{1,2,3,4}.png` into `examples/map.png`.

Channelpack processes text definition files with lines of the form

```
CCCC = filename.png PPPP
```

where `C` is one of `rgba` and `P` is a valid value of `C` or a "pseudo-channel" `AmM`. Right now the counts of `C` and
`P` must be equal and between 1-4.

These rules are used to construct a PNG image with the same stem as the definition file and a `.png` extension.

For example, a file map.txt

```
r = ./map1.png r
g = ./map2.png r
b = ./map3.png r
a = ./map4.png r
```

results in a texture with a red channel copied from red of map1.png, green channel copied from red of map2.png, blue
channel copied from red of map3.png, and alpha channel copied from red of map4.png.

Here is another example which:

- Packs red & green of map1.png into red & green of map.png
- Packs red & green of map2.png into blue & alpha of map.png

```
rg = ./map1.png rg
ba = ./map2.png rg
```

Finally, this file swizzles rgb of map1.png -> bgr of map.png:

```
rgb = ./map1.png bgr
```

## TODO

- [x] Swizzle (`rgb = texture.png bgr`)
- [ ] Combine (`a = texture.png rb mean`)
- [ ] Copy (`rgba = texture.png r`, same as `rgba = texture.png rrrr`)
- [ ] Other texture formats
- [ ] Proper CLI
- [ ] Comment & arbitrary whitespace support in definition file
- [ ] Documentation
- [ ] Unity importer/C# implementation
- [ ] GUI
