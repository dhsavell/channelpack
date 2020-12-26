from PIL import Image
import numpy as np
import enum
import pathlib
import sys
import os


CHANNELS = "rgba"
PSEUDO_CHANNELS = {
    "A": (lambda im: np.mean(im, axis=2), "Average of all channels"),
    "M": (lambda im: np.max(im, axis=2), "Maximum of all channels"),
    "m": (lambda im: np.min(im, axis=2), "Minimum of all channels"),
}


def map_channels(src: np.ndarray, src_map: str, dst: np.ndarray, dst_map: str, combine=np.mean):
    """
    Map_channels writes certain channels of the input (src) to certain channels of the output (dst).

    Inputs are decided by src_map. Src_map is a string of channels (r, g, b, a) and "pseudo-channels" (i.e. A for the
    average of all channels).

    Outputs are defined by dst_map, which works similarly. Dst_map is a string of unique channels (r, g, b, a).

    Both src_map and dst_map are inclusively between 1 and 4 characters long. Map_channels has three behaviours based
    on the lengths of src_map and dst_map.

        1. If len(src_map) == len(dst_map), channels will be mapped one-to-one.

            Examples:
                src_map     dst_map     behavior
                rg          ba          write src red to dst blue and src green to dst alpha
                rrrr        rgba        write src red to all four dst channels
                AAAA        rgba        write average of channels in src to all four dst channels
                rrrrr       rgba        invalid (src_map too long)
                rrrr        A           invalid (pseudo-channels cannot be used in dst_map)
                rgba        rrrr        invalid (dst_map channels must be unique)

        2. If len(src_map) > 1 and len(dst_map) == 1, channels will be combined using the function given in the optional
           "combine" parameter. Combine is called with arguments (ndarray, axis=2) to match most numpy functions.

            Examples:
                src_map     dst_map     combine     behavior
                rgba        r           np.mean     writes average of all channels in src to dst red (equal to A -> r)
                rgba        r           np.max      writes maximum of all channels in src to dst red (equal to M -> r)
                gb          r           np.max      writes maximum of (red, green) in src to dst red

        3. If len(src_map) == 1 and len(dst_map) > 1, one channel will be copied.

            Examples:
                src_map     dst_map     behavior
                r           rgba        copies src red into all four dst channels (equal to rrrr -> rgba)
                g           rgb         copies src green into dst rgb channels

    Note that len(src_map) != len(dst_map) with both len(src_map) > 1 and len(dst_map) > 1 is not a valid mapping due
    to its ambiguity. A grouping operator would make this possible, but we won't implement one until there is a
    demonstrated need.
    """

    if len(src_map) == len(dst_map):
        for (src_ch, dst_ch) in zip(src_map, dst_map):
            if dst_ch not in CHANNELS:
                raise ValueError(f"Unknown channel {dst_ch}")

            res = None
            if src_ch in CHANNELS:
                res = src[..., CHANNELS.index(src_ch)]
            elif src_ch in PSEUDO_CHANNELS:
                res = PSEUDO_CHANNELS[src_ch][0](src)

            dst[..., CHANNELS.index(dst_ch)] = res

    elif len(src_map) > 1 and len(dst_map) == 1:
        raise NotImplementedError()

    elif len(src_map) == 1 and len(dst_map) > 1:
        raise NotImplementedError()

    else:
        raise ValueError(f"Channel mapping {src_map} -> {dst_map} is ambiguous")


def map_from_file(path: pathlib.Path):
    components = path.open("r").readlines()
    os.chdir(path.parent)
    dst_path = path.stem + '.png'

    maps = dict()
    dst = None

    for i, line in enumerate(components):
        try:
            dst_map, eq, src, src_map, *_ = line.split()
            assert eq == '='
        except:
            print(f'{path}:{i}:', 'expected format `cccc = filename cccc`', file=sys.stderr)
            return

        ar = None
        if src not in maps:
            try:
                ar = maps[src] = np.asarray(Image.open(src).convert("RGBA"))
            except:
                print(f'{path}:{i}:', f'failed to open file {src}', file=sys.stderr)
                return

        else:
            ar = maps[src]

        if dst is None:
            dst = np.full((ar.shape[0], ar.shape[1], 4), 255, dtype=np.uint8)

        map_channels(ar, src_map, dst, dst_map)

    if dst is None:
        print(str(path) + ':', 'file must have at least one line', file=sys.stderr)
        return

    Image.fromarray(dst).save(dst_path)
    print(f"Saved to {dst_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: channelpack [filename.txt]")
    
    path = pathlib.Path(sys.argv[1])
    if not path.exists() or not path.is_file():
        sys.exit(f"Error: {path} does not exist or is not a file")

    map_from_file(pathlib.Path(sys.argv[1]))
