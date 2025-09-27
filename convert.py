import img2pdf as im
import PIL
import os

def create_folder(folder_dir):
    try:
        os.mkdir(folder_dir)
    except FileExistsError:
        print("Folder already exists")
    except PermissionError:
        print("Permission denied. OS said no, try another directory for the folder")
    except Exception as e:
        print(f"an exception occured: {e}")

def convert_single_image_to_pdf(image_dir, output_folder):
    create_folder(output_folder)
    image = PIL.Image.open(image_dir)
    pdf_bytes = im.convert(image.filename)
    file = open(output_folder + f"/{image.filename.split('.')[0]}.pdf", 'wb')
    file.write(pdf_bytes)
    image.close()
    file.close()
    print("converted image successfully")

def generate_image_list(images_dir_folder):
    images = []
    for fname in os.listdir(images_dir_folder):
        if not fname.endswith((".jpg", ".png", ".jpeg")):
            continue
        
        path = os.path.join(images_dir_folder, fname)
        if(os.path.isdir(path)):
            continue
        images.append(path)
    images.sort()
    return images

#this grabs the images in a folder and sorts them before conversion
def convert_multiple_images(images, output_folder, filename):
    create_folder(output_folder)
    with open(f"{output_folder}/{filename}.pdf", "wb") as f:
        f.write(im.convert(images))
    
def create_output_file_name(images_dir_folder):
    if '/' in images_dir_folder:
        return images_dir_folder.split('/')[-1]
    else:
        return images_dir_folder.split("\\")[-1]
    

convert_multiple_images(generate_image_list("snek"), "sponge", "ching cheng hanji")