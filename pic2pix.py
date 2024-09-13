from PIL import Image, ImageEnhance
import numpy as np
import time, math, sys



def convert(source_img_path,palette = ''):
    '''
    This is the main conversion function
    
    source_img_path: The location of the file to be converted
    palette: An optional color palette to be applied to the function

    returns: A filtered image
    '''
    
    with Image.open(source_img_path) as img:
        w, h = img.size 

        #TURN IMAGE INTO A SQUARE BY CROPPING OUT SIDES
        if w > h:
            bdr = (w - h)//2
            crp_img = img.crop((bdr, 0, w - bdr, h))
            img = crp_img
            w = h
        
        #REDUCE RESOLUTION
        while w > 1000 or h > 1000: 
            w, h = w//2, h//2
            reduced_size = (w,h)
            img = img.resize(reduced_size)
        
        if (img.mode != 'RGBA'): #RGBA mode allows transparency
            img = img.convert('RGBA')

        np_img = np.array(img) #numpy for quicker processing

        #These values should be customizable (maybe sliders?)
        TOLERANCE = 40 #Acceptable degree of pixel difference
        SAMPLER = 25 #Size of sampling area in pixels
        COLOR = 1.1 #Color Enhancement
        SHARP = 2 #Sharpness ENhancement

        #SAMPLE 4 CORNERS OF THE IMAGE
        sample = [
            np.array(img.crop((0, 0, SAMPLER, SAMPLER))),
            np.array(img.crop((w-SAMPLER, 0, w, SAMPLER))),
            np.array(img.crop((0, h-SAMPLER, SAMPLER, h))),
            np.array(img.crop((w-SAMPLER, h-SAMPLER, w, h)))
            ]
        comp = [np.mean(i, axis = (0,1)) for i in sample]
        low = [np.maximum(i - TOLERANCE, 0) for i in comp] #RGB must be 0 < r,g,b < 255
        high = [np.minimum(i + TOLERANCE, 255) for i in comp]

        for i in np_img: #for each row of pixels in the image
            for j in i: #for each element in a row
                for i in range(4): #compare  w/4 sampled corner means
                    if (low[i][0] <= j[0] <= high[i][0]) and (low[i][1] <= j[1] <= high[i][1]) and (low[i][2] <= j[2] <= high[i][2]):
                        j[3] = 0 #Turn pixel transparent
                        break
                    else:
                        j[3] = 255
                        if 'pencil' in source_img_path: # PENCIL TEST
                            j[0],j[1],j[2] = 0, 0, 0
                    
        trp_img = Image.fromarray(np_img)
        trp_img.save('transparency_test2.png') #png has transparency
        trp_img.show()
        if 'pencil' in source_img_path:
            sys.exit()


        #TIME TO PIXELLATE
        rdc_img = trp_img.resize((128,128),Image.BILINEAR)
        rsz_img = rdc_img.resize(trp_img.size, Image.NEAREST)
        rsz_img = np.array(rsz_img)

        #Change border color to black

        for i in rsz_img:
            for j in i:
                if j[3] < 255:
                    j[0], j[1], j[2] = 0,0,0

        cor_img = Image.fromarray(rsz_img)

        col_plus = ImageEnhance.Color(cor_img) 
        col_fin = col_plus.enhance(COLOR)

        shp_plus = ImageEnhance.Sharpness(col_fin)
        fin = shp_plus.enhance(SHARP)

        con_plus = ImageEnhance.Contrast(fin)
        finished_product = con_plus.enhance(1.1)

        finished_product.show()

    if palette: #Open palette sample image and store its values in an numpy array for later application
        apply_palette(fin, palette)

    cor_img.save('corrected_img.png')
    fin.save('walk5.png')
    pass


import numpy as np
from PIL import Image

def apply_palette(img, palette):
    '''
    This function applies a color palette, if one is provided. A default palette, fantasy24 is embedded in the code.
    img: A filtered image produced by the convert function
    palette: An optional color palette to be applied to the image

    returns: The image output from convert function with an applied color palette
    '''
    
    np_img_array = np.array(img)
    np_copy_array = np.array(img)
    np_palette = np.array(palette)

    alpha_mask = np_img_array[:, :, 3] != 0 #specifies a mask that checks all pixels and sets to False those pixels that have alpha channel == 0

    img_rgb = np_img_array[:, :, :3] #Cutting out the alpha channel from the pixels, changing shape from (w,h,4) tp (w,h,3)
    
    img_rgb_opaque = img_rgb[alpha_mask] #we're onoly processing pixels with non zero alpha value. Note that this removes all the pixels with alpha == 0, and flattens the array into a 2D array from a 3D one

    # Compute all pairwise distances between image RGB values and palette RGB values
    img_rgb_opaque_modded = img_rgb_opaque[:, np.newaxis, :]  # Shape: (num_opaque_pixels, 1, 3). Here. np.newaxis is a special placeholder dimension to help in broadcasting vs palette array

    palette_expanded = np_palette[np.newaxis, :, :]  # Shape: (1, len(palette), 3). Here too, we modify the palette array with the placeholder dimension.
    #Why add newaxis to both? To ensure the only operations that matter take place and the other dimensions do not interact with each othrr

    distances = np.sqrt(np.sum((img_rgb_opaque_modded - palette_expanded) ** 2, axis=-1))  # Shape: (num_opaque_pixels, len(palette)). Here, the 2nd dimension holds the actual distances.
    
    min_indices = np.argmin(distances, axis=-1)  # Shape: (num_opaque_pixels), min_indices stores the index of each palette color for each opaque pixel.
    
    # Map the closest palette colors to the image
    np_copy_array[alpha_mask, :3] = np_palette[min_indices]  # Assign RGB values. The mask is applied and channels(rgb) specified, then, np_palette[min_indices] selectively replaces those rgb values with the palette colors
    
    # Convert back to an image
    recolored_img = Image.fromarray(np_copy_array)
    recolored_img.show()
    recolored_img.save('Sprited.png')



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
    [48, 15, 10]
]
    source = input('Enter source image path: ')

    start = time.time()
    convert(source,palette)
    end = time.time()
    print(f'Time taken to pixellate: {end - start}')

    pass



if __name__ == "__main__":
    main()
    print('Cleared!')
