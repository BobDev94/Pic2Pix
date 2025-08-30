from PIL import Image, ImageEnhance
import numpy as np
import time, math, sys, os, argparse


class SmartFormatter(
    argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    pass


def uint8(s: str) -> int:
    try:
        v = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a valid number")
    if not (0 <= v <= 255):
        raise argparse.ArgumentTypeError("must be 0–255")
    return v


def posint(s: str) -> int:
    try:
        v = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a valid number")
    if v <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return v


def fps_range(s: str) -> float:
    try:
        v = float(s)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a valid number")
    if not (0.1 <= v <= 240):
        raise argparse.ArgumentTypeError("FPS must be 0.1–240")
    return v


def duration_range(s: str) -> int:
    try:
        v = int(s)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a valid number")
    if not (1 <= v <= 20000):
        raise argparse.ArgumentTypeError("duration must be 1–20000 ms")
    return v


def convert(source: str, palette: list[list[int]], tolerance: int = 40) -> None:
    """
    This is the main conversion function

    source_img_path: The location of the file to be converted
    palette: An optional color palette to be applied to the function

    returns: A filtered image
    """
    source_img_path = source
    palette_list = palette

    # Determine output dir and base name
    output_dir = None
    base_name = None
    if hasattr(convert, "output_dir"):
        output_dir = convert.output_dir
    if hasattr(convert, "base_name"):
        base_name = convert.base_name

    with Image.open(source_img_path) as img:
        w, h = img.size

        # TURN IMAGE INTO A SQUARE BY CROPPING OUT SIDES
        if w > h:
            bdr = (w - h) // 2
            crp_img = img.crop((bdr, 0, w - bdr, h))
            img = crp_img
            w = h

        # REDUCE RESOLUTION
        while w > 1000 or h > 1000:
            w, h = w // 2, h // 2
            reduced_size = (w, h)
            img = img.resize(reduced_size)

        if img.mode != "RGBA":  # RGBA mode allows transparency
            img = img.convert("RGBA")

        np_img = np.array(img)  # numpy for quicker processing

        # TODO: These values should be customizable (sliders if gui?)
        TOLERANCE = tolerance  # Acceptable degree of pixel difference
        SAMPLER = 25  # Size of sampling area in pixels
        COLOR = 1.1  # Color Enhancement
        SHARP = 2  # Sharpness Enhancement

        # SAMPLE 4 CORNERS OF THE IMAGE
        sample = [
            np.array(img.crop((0, 0, SAMPLER, SAMPLER))),
            np.array(img.crop((w - SAMPLER, 0, w, SAMPLER))),
            np.array(img.crop((0, h - SAMPLER, SAMPLER, h))),
            np.array(img.crop((w - SAMPLER, h - SAMPLER, w, h))),
        ]
        comp = [np.mean(i, axis=(0, 1)) for i in sample]
        low = [
            np.maximum(i - TOLERANCE, 0) for i in comp
        ]  # RGB must be 0 < r,g,b < 255
        high = [np.minimum(i + TOLERANCE, 255) for i in comp]

        for i in np_img:  # for each row of pixels in the image
            for j in i:  # for each element in a row
                for i in range(4):  # compare  w/4 sampled corner means
                    if (
                        (low[i][0] <= j[0] <= high[i][0])
                        and (low[i][1] <= j[1] <= high[i][1])
                        and (low[i][2] <= j[2] <= high[i][2])
                    ):
                        j[3] = 0  # Turn pixel transparent
                        break
                    else:
                        j[3] = 255
                        if "pencil" in source_img_path:  # PENCIL TEST
                            j[0], j[1], j[2] = 0, 0, 0

        trp_img = Image.fromarray(np_img)
        # Only save transparency image for --file and --folder
        if output_dir and base_name:
            trp_img.save(os.path.join(output_dir, f"{base_name}_transparency.png"))
            trp_img.show()
        # For spritesheet, skip saving transparency image
        if "pencil" in source_img_path:
            sys.exit()

        # TIME TO PIXELLATE
        rdc_img = trp_img.resize((128, 128), Image.BILINEAR)
        rsz_img = rdc_img.resize(trp_img.size, Image.NEAREST)
        rsz_img = np.array(rsz_img)

        # Change border color to black

        for i in rsz_img:
            for j in i:
                if j[3] < 255:
                    j[0], j[1], j[2] = 0, 0, 0

        cor_img = Image.fromarray(rsz_img)

        col_plus = ImageEnhance.Color(cor_img)
        col_fin = col_plus.enhance(COLOR)

        shp_plus = ImageEnhance.Sharpness(col_fin)
        fin = shp_plus.enhance(SHARP)

        con_plus = ImageEnhance.Contrast(fin)
        finished_product = con_plus.enhance(1.1)

        finished_product.show()

    if (
        palette
    ):  # Open palette sample image and store its values in an numpy array for later application
        apply_palette(fin, palette)

        if output_dir and base_name:
            cor_img.save(os.path.join(output_dir, f"{base_name}_corrected.png"))
            fin.save(os.path.join(output_dir, f"{base_name}_walk5.png"))
        # Only save these files for --file and --folder modes
    pass


def apply_palette(img, palette):
    """
    This function applies a color palette, if one is provided. A default palette, fantasy24 is embedded in the code.
    img: A filtered image produced by the convert function
    palette: An optional color palette to be applied to the image

    returns: The image output from convert function with an applied color palette
    """

    np_img_array = np.array(img)
    np_copy_array = np.array(img)
    np_palette = np.array(palette)

    alpha_mask = (
        np_img_array[:, :, 3] != 0
    )  # specifies a mask that checks all pixels and sets to False those pixels that have alpha channel == 0

    img_rgb = np_img_array[
        :, :, :3
    ]  # Cutting out the alpha channel from the pixels, changing shape from (w,h,4) tp (w,h,3)

    img_rgb_opaque = img_rgb[
        alpha_mask
    ]  # we're only processing pixels with non zero alpha value. Note that this removes all the pixels with alpha == 0, and flattens the array into a 2D array from a 3D one

    # Compute all pairwise distances between image RGB values and palette RGB values
    img_rgb_opaque_modded = img_rgb_opaque[
        :, np.newaxis, :
    ]  # Shape: (num_opaque_pixels, 1, 3). Here. np.newaxis is a special placeholder dimension to help in broadcasting vs palette array

    palette_expanded = np_palette[
        np.newaxis, :, :
    ]  # Shape: (1, len(palette), 3). Here too, we modify the palette array with the placeholder dimension.
    # Why add newaxis to both? To ensure the only operations that matter take place and the other dimensions do not interact with each othrr

    distances = np.sqrt(
        np.sum((img_rgb_opaque_modded - palette_expanded) ** 2, axis=-1)
    )  # Shape: (num_opaque_pixels, len(palette)). Here, the 2nd dimension holds the actual distances.

    min_indices = np.argmin(
        distances, axis=-1
    )  # Shape: (num_opaque_pixels), min_indices stores the index of each palette color for each opaque pixel.

    # Map the closest palette colors to the image
    np_copy_array[alpha_mask, :3] = np_palette[
        min_indices
    ]  # Assign RGB values. The mask is applied and channels(rgb) specified, then, np_palette[min_indices] selectively replaces those rgb values with the palette colors

    # Convert back to an image
    recolored_img = Image.fromarray(np_copy_array)
    recolored_img.show()
    # Only save sprited image if output_dir and base_name are set (not None)
    # TODO --output_dir flag?
    if (
        hasattr(apply_palette, "output_dir")
        and hasattr(apply_palette, "base_name")
        and apply_palette.output_dir
        and apply_palette.base_name
    ):
        recolored_img.save(
            os.path.join(
                apply_palette.output_dir, f"{apply_palette.base_name}_sprited.png"
            )
        )
    elif not (
        hasattr(apply_palette, "output_dir") and hasattr(apply_palette, "base_name")
    ):
        recolored_img.save("Sprited.png")
    # Otherwise, skip saving for spritesheet mode


def main():

    palette = [
        [31, 36, 10],
        [57, 87, 28],
        [165, 140, 39],
        [239, 172, 40],
        [239, 216, 161],
        [171, 92, 28],
        [24, 63, 57],
        [239, 105, 47],
        [239, 183, 117],
        [165, 98, 67],
        [119, 52, 33],
        [114, 65, 19],
        [42, 29, 13],
        [57, 42, 28],
        [104, 76, 60],
        [146, 126, 106],
        [39, 100, 104],
        [239, 58, 12],
        [60, 159, 156],
        [155, 26, 10],
        [54, 23, 12],
        [85, 15, 10],
        [48, 15, 10],
    ]

    def uint8(s: str) -> int:
        v = int(s)
        if not (0 <= v <= 255):
            raise argparse.ArgumentTypeError("must be 0–255")
        return v

    def posint(s: str) -> int:
        v = int(s)
        if v <= 0:
            raise argparse.ArgumentTypeError("must be > 0")
        return v

    parser = argparse.ArgumentParser(
        prog="pic2pix",
        description="Pic2Pix image processor",
        formatter_class=SmartFormatter,
        epilog="""Examples:
  pic2pix file ./image.png
  pic2pix folder ./frames --tolerance 32
  pic2pix spritesheet ./sheet.png --rows 4 --columns 6
  pic2pix gif ./frames --fps 12
  pic2pix gif ./frames --duration 80
""",
    )

    # Command options
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--tolerance",
        type=uint8,
        default=40,
        metavar="0-255",
        help="Transparency tolerance",
    )

    sub = parser.add_subparsers(
        dest="command", required=False, title="commands", metavar="<command>"
    )

    # pic2pix file FILE
    # keeps args.file
    p_file = sub.add_parser(
        "file", parents=[common], help="Process a single image file"
    )
    p_file.add_argument("file", help="Path to an image file")

    # pic2pix folder FOLDER
    # keeps args.folder
    p_folder = sub.add_parser(
        "folder", parents=[common], help="Process all images in a folder"
    )
    p_folder.add_argument("folder", help="Folder containing images")

    # pic2pix spritesheet SPRITESHEET --rows N --columns M
    # keeps args.spritesheet/rows/columns
    p_sheet = sub.add_parser(
        "spritesheet", parents=[common], help="Process a spritesheet image"
    )
    p_sheet.add_argument("spritesheet", help="Spritesheet image file")
    p_sheet.add_argument(
        "--rows", type=posint, required=True, help="Rows in spritesheet grid"
    )
    p_sheet.add_argument(
        "--columns",
        "--cols",
        dest="columns",
        type=posint,
        required=True,
        help="Columns in spritesheet grid",
    )

    # pic2pix gif FOLDER [--fps X | --duration MS]
    # keeps args.gif
    p_gif = sub.add_parser(
        "gif", parents=[common], help="Create animated GIF from images in a folder"
    )
    p_gif.add_argument("gif", help="Folder of input frames (sorted by name)")
    g = p_gif.add_mutually_exclusive_group()
    g.add_argument("--fps", type=float, default=12, help="Frames per second")
    g.add_argument(
        "--duration", type=int, metavar="MS", help="Frame duration in milliseconds"
    )

    args = parser.parse_args()

    # Show help if no subcommand provided
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    tolerance = args.tolerance

    base_output_dir = "output"
    os.makedirs(base_output_dir, exist_ok=True)

    if args.command == "spritesheet":
        spritesheet_dir = os.path.join(base_output_dir, "spritesheet")
        os.makedirs(spritesheet_dir, exist_ok=True)
        sheet_filename = os.path.splitext(os.path.basename(args.spritesheet))[0]
        sheet_folder = os.path.join(spritesheet_dir, sheet_filename)
        os.makedirs(sheet_folder, exist_ok=True)
        print(
            f"Processing spritesheet: {args.spritesheet} ({args.rows} rows x {args.columns} columns)"
        )
        with Image.open(args.spritesheet) as sheet:
            sheet_w, sheet_h = sheet.size
            sprite_w = sheet_w // args.columns
            sprite_h = sheet_h // args.rows
            for r in range(args.rows):
                for c in range(args.columns):
                    left = c * sprite_w
                    upper = r * sprite_h
                    right = left + sprite_w
                    lower = upper + sprite_h
                    sprite = sheet.crop((left, upper, right, lower))
                    sprite_name = f"{sheet_filename}_r{r}_c{c}"
                    sprite_path = os.path.join(sheet_folder, f"{sprite_name}.png")
                    sprite.save(sprite_path)
                    print(f"Processing sprite {sprite_path}")
                    start = time.time()
                    # Do not save extra outputs for spritesheet
                    convert.output_dir = None
                    convert.base_name = None
                    apply_palette.output_dir = None
                    apply_palette.base_name = None
                    convert(sprite_path, palette, tolerance=tolerance)
                    end = time.time()
                    print(f"Time taken: {end - start:.2f}s\n")

    elif args.command == "folder":
        folder_dir = os.path.join(base_output_dir, "folder")
        os.makedirs(folder_dir, exist_ok=True)
        img_exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")
        files = [
            os.path.join(args.folder, f)
            for f in os.listdir(args.folder)
            if f.lower().endswith(img_exts)
        ]
        print(f"Processing {len(files)} images in folder: {args.folder}")
        for source in files:
            print(f"Processing {source}")
            start = time.time()
            image_name = os.path.splitext(os.path.basename(source))[0]
            image_folder = os.path.join(folder_dir, image_name)
            os.makedirs(image_folder, exist_ok=True)
            convert.output_dir = image_folder
            convert.base_name = image_name
            apply_palette.output_dir = image_folder
            apply_palette.base_name = image_name
            convert(source, palette, tolerance=tolerance)
            end = time.time()
            print(f"Time taken: {end - start:.2f}s\n")

    elif args.command == "file":
        file_dir = os.path.join(base_output_dir, "file")
        os.makedirs(file_dir, exist_ok=True)
        print(f"Processing single file: {args.file}")
        start = time.time()
        image_name = os.path.splitext(os.path.basename(args.file))[0]
        image_folder = os.path.join(file_dir, image_name)
        os.makedirs(image_folder, exist_ok=True)
        convert.output_dir = image_folder
        convert.base_name = image_name
        apply_palette.output_dir = image_folder
        apply_palette.base_name = image_name
        convert(args.file, palette, tolerance=tolerance)
        end = time.time()
        print(f"Time taken: {end - start:.2f}s")

    elif args.command == "gif":
        gif_dir = os.path.join(base_output_dir, "gif")
        os.makedirs(gif_dir, exist_ok=True)
        img_exts = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")
        files = [
            os.path.join(args.gif, f)
            for f in sorted(os.listdir(args.gif))
            if f.lower().endswith(img_exts)
        ]
        if not files:
            print(f"No images found in {args.gif}")
            sys.exit(1)

        print(f"Creating animated GIF from {len(files)} images in {args.gif}")
        images = []
        for file_path in files:
            try:
                img = Image.open(file_path)
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                images.append(img)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue

        if images:
            gif_name = f"{os.path.basename(args.gif)}_animated.gif"
            gif_path = os.path.join(gif_dir, gif_name)
            duration = args.duration if args.duration else int(1000 / args.fps)
            images[0].save(
                gif_path,
                save_all=True,
                append_images=images[1:],
                duration=duration,
                loop=0,
            )
            print(f"Animated GIF saved to: {gif_path}")
        else:
            print("No valid images to create GIF")


if __name__ == "__main__":
    main()
    print("Cleared!")
