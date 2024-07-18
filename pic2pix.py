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
    
    with Image.open(source_img_path) as img: #.open reads image from file
        w, h = img.size #loading pic width and height. 

        if w > h: #Make the picture into a square, if width > height, this is mostly just for convenience
            bdr = (w - h)//2
            x1, y1, x2, y2 = bdr, 0, w - bdr, h
            crp_img = img.crop((x1, y1, x2, y2))
            crp_img.save('cropped.jpg')
            img = crp_img
            w = h
        
        while w > 1000 or h > 1000: #reducing resolution massively reduces processing time. Higher resolutions can take upwards of minutes to process.
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

        #Take 4 corner samples and analyze. A single corner would most likely be sufficient, but shadows and shading makes this necessary
        sample = [
            np.array(img.crop((0, 0, SAMPLER, SAMPLER))),
            np.array(img.crop((w-SAMPLER, 0, w, SAMPLER))),
            np.array(img.crop((0, h-SAMPLER, SAMPLER, h))),
            np.array(img.crop((w-SAMPLER, h-SAMPLER, w, h)))
            ]
        comp = [np.mean(i, axis = (0,1)) for i in sample]
        low = [np.maximum(i - TOLERANCE, 0) for i in comp]
        high = [np.minimum(i + TOLERANCE, 255) for i in comp]

        for i in np_img: #for each row of pixels in the image
            for j in i: #for each element in a row
                for i in range(4): #compare  w/4 sampled corner means
                    if (low[i][0] <= j[0] <= high[i][0]) and (low[i][1] <= j[1] <= high[i][1]) and (low[i][2] <= j[2] <= high[i][2]):
                        j[3] = 0
                        break
                    else:# PENCIL TEST
                        j[3] = 255
                        if 'pencil' in source_img_path:
                            j[0],j[1],j[2] = 0, 0, 0
                    
        trp_img = Image.fromarray(np_img)
        trp_img.save('transparency_test2.png') #png has transparency
        trp_img.show()
        if 'pencil' in source_img_path:
            sys.exit()


        #TIME TO PIXELLATE
        rdc_img = trp_img.resize((88,88),Image.BILINEAR)
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
        finished_product = con_plus.enhance(1.3)

        finished_product.show()

    if palette: #Open palette sample image and store its values in an numpy array for later application
        
        if type(palette) == str:
            #FIRST NEED TO EXTRACT PALETTE COLORS
            with Image.open('palette.jpg') as pal:

                np_pal = np.array(pal)
                one_d_pal = np_pal.reshape(pal.size[0] * pal.size[1], 3)#2D array --> 1D array, 1st element is number elements in row, second is number of elements in each actual array

                cluster = [[one_d_pal[0]]]
                dist = 40
                for i in one_d_pal: #for every pixel
                    ip = 0
                    for j in cluster: #for every cluster
                        if i[0] - dist < j[0][0] <  i[0] + dist and i[1] - dist < j[0][1] < i[1] + dist and i[2] - dist < j[0][2] < i[2] + dist: # they belong in same cluster if 1
                            j.append(i)
                            ip = 1
                            break 
                    if not ip:
                        cluster.append([i])

                averaged_values = []
                for x in cluster:
                    single_list = np.array(x)
                    avg = np.mean(single_list, axis = 0)
                    averaged_values.append(np.round(avg))
        
        elif type(palette) == list:
            averaged_values = palette
            
        apply_palette(fin, averaged_values)

    cor_img.save('corrected_img.png')
    fin.save('walk5.png')
    pass



def apply_palette(img,palette):
    '''
    This function applies a color palette, if one is provided. A default palette, fantasy24 is embedded in the code
    img: A filtered image produced by the convert function
    palette: An optional color palette to be applied to the image

    returns: The image output from convert function with an applied color palette
    '''

    np_img_array = np.array(img)
    np_copy_array = np.array(img)
    np_palette = np.array(palette)

    row = np_img_array.shape[0]
    col = np_img_array.shape[1]

    for i in range(row):
        for j in range(col):
            dist_index = []
            if np_img_array[i][j][3] != 0: #only calculate for opaque
                for k in range(len(np_palette)):
                    dist_index.append(math.dist(np_img_array[i][j][:3], np_palette[k]))
                ind = dist_index.index(min(dist_index))

                brr = np.append(palette[ind], 255)
                np_copy_array[i][j] = brr
    
    recolored_img = Image.fromarray(np_copy_array)
    recolored_img.show()
    recolored_img.save('Sprited.png')

    pass



def main():

    start = time.time()

    palette = 'palette.jpg'
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
    convert(source,palette)

    end = time.time()
    print(f'Time taken to pixellate: {end - start}')

    pass



if __name__ == "__main__":
    main()
    print('Cleared!')
