import re, io
import img2pdf as im
import PIL
import os, sys
from PyQt6.QtCore import QSize
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
import messages
#add the filters so that the save file type is automatically a pdf
def extract_numbers(stringlist):
    match = re.search(r'(\d+)(?=\.\w+$)', stringlist)
    return int(match.group()) if match else float('inf')

def create_folder(folder_dir):#forgot what this function was used for
    try:
        os.mkdir(folder_dir)
    except FileExistsError:
        print("Folder already exists")
    except PermissionError:
        print("Permission denied. OS said no, try another directory for the folder")
    except Exception as e:
        print(f"an exception occured: {e}")

def convert_single_image_to_image_without_alpha(image_dir):
    image = PIL.Image.open(image_dir)
    pdf_bytes = None
    if image.mode == 'RGBA':
        rgbImage = PIL.Image.new("RGB", image.size, (255, 255, 255))
        rgbImage.paste(image, mask=image.split()[3])
        inMemoryFile = io.BytesIO()
        rgbImage.save(inMemoryFile, format="PNG")
        imageBytes = inMemoryFile.getvalue()
        pdf_bytes = im.convert(imageBytes, rotation=im.Rotation.ifvalid)
        return pdf_bytes
    else:
        pdf_bytes = im.convert(image.filename, rotation=im.Rotation.ifvalid)
        return pdf_bytes
        

#sorts by default
def generate_image_list(images_dir_folder, sort_pictures=True):
    images = []
    for fname in os.listdir(images_dir_folder):
        if not fname.endswith((".jpg", ".png", ".jpeg", ".webp")):
            continue
        
        path = os.path.join(images_dir_folder, fname)
        if(os.path.isdir(path)):
            continue
        images.append(path)
    if sort_pictures == True:
        images.sort(key=extract_numbers)
    return images

#this grabs the images in a folder and sorts them before conversion
def convert_multiple_images(images, output_folder, filename):
    if len(images) !=0:
        create_folder(output_folder)
        with open(f"{output_folder}/{filename}.pdf", "wb") as f:
            try:
                f.write(im.convert(images), rotation=im.Rotation.ifvalid)
            except im.AlphaChannelError as alphaError:
                print(alphaError)
                for image in images:
                    f.write(convert_single_image_to_image_without_alpha(image))
    
def create_output_file_name(images_dir_folder):
    if '/' in images_dir_folder:
        return images_dir_folder.split('/')[-1]
    else:
        return images_dir_folder.split("\\")[-1]
    
def convert_multiple_images_with_specified_file_path(images, filepath):
    if len(images) != 0:
        with open(filepath, "wb") as f:
            try:
                f.write(im.convert(images, rotation=im.Rotation.ifvalid))
            except im.AlphaChannelError as alphaError:
                print(alphaError)
                for image in images:
                    f.write(convert_single_image_to_image_without_alpha(image))
    
class ConvertorUI(QtWidgets.QMainWindow):
    globalImageList = []
    folder = None #use this if the user opened a filder first, otherwise they must specify the directory and details when it is time to save a pdf
    isInFolderMode = False #use his as a flag to see if we need to save the folder path
    defaultFileDirectoryText =  None
    
    def __init__(self):
        super(ConvertorUI, self).__init__()
        uic.loadUi("convertorUI.ui", self)
        self.show()
        self.defaultFileDirectoryText = self.lblFileDirectory.text()
        #Image models
        
        self.tblImagesList.setFlow(QtWidgets.QListView.Flow.TopToBottom)
        self.tblImagesList.setMovement(QtWidgets.QListView.Movement.Snap)
        self.tblImagesList.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        self.tblImagesList.setGridSize(QSize(120, 120))
        self.tblImagesList.setIconSize(QSize(120,120))
        self.tblImagesList.setDragDropOverwriteMode(False)
        self.tblImagesList.setSpacing(10)
        self.tblImagesList.setDragEnabled(True)
        self.tblImagesList.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tblImagesList.setAcceptDrops(True)
        self.tblImagesList.setDropIndicatorShown(True)
        self.tblImagesList.setWrapping(False)
        #add the function bindings
        self.btnOpenFolder.clicked.connect(self.btnOpenFolderFunction)
        self.btnOpenImage.clicked.connect(self.openImage)
        self.btnAddFolder.clicked.connect(self.addFolder)
        self.btnAddImage.clicked.connect(self.addImage)
        self.btnSavePDF.clicked.connect(self.btnSaveFileFunction)
        self.btnBatch.clicked.connect(self.batch_Mode_function)
    
    def addImage(self):
        self.openFile(add_to_existing_list=True)
        self.addImagesToListView()
              
    def addFolder(self):
        self.openFolder(add_to_existing_list=True)
        self.addImagesToListView()
    
    def openImage(self):
        self.openFile(add_to_existing_list=False)
        self.folder = None
        self.isInFolderMode = False
        self.addImagesToListView()
    
    def btnOpenFolderFunction(self):
        self.isInFolderMode = False
        self.folder = None
        self.openFolder(add_to_existing_list=False)
        self.addImagesToListView()
    
    def btnSaveFileFunction(self):
        imagesList = self.getImages()
                
        if self.isInFolderMode:
            message = "Do you wish to specify the file name and folder it will be save in?"
            title = "Hmm :/"
            specifyOutputFileConfirmation = messages.display_option_message(message=message, title=title)
            if specifyOutputFileConfirmation:#assuming its in folder mode
                filepath = self.saveFileDialog()  
                convert_multiple_images_with_specified_file_path(images=imagesList, filepath=filepath)
                messages.display_message(f"PDF created sucessfully. File is found at {filepath}", "yay", messages.INFO_MSG)
        
            else: #still assuming folder mode
                filename = create_output_file_name(self.folder)
                convert_multiple_images(imagesList, self.folder, filename)
                title = "Yeeeeeeeeaaaaaaaaaaaaaah"
                message = f"PDF created successfully. File is found at {self.folder}/{filename}.pdf"
                messages.display_message(message=message, title=title, message_type=messages.INFO_MSG)
        else: 
            #is in single file mode. use will specify the output directory (meaning the user didnt click the open folder button first)
            filepath = self.saveFileDialog()  
            convert_multiple_images_with_specified_file_path(images=imagesList, filepath=filepath)
            messages.display_message("Job done comrade", "yay", messages.INFO_MSG)         
          
    def openFileDialogue(self, folder_mode=True):
        dialog = QtWidgets.QFileDialog(self)
        if folder_mode:
            dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        else:
            dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)
        dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.List)
        if dialog.exec():
            filenames = dialog.selectedFiles()
            if(folder_mode == True):
                self.lblFileDirectory.setText(self.defaultFileDirectoryText + ": " + filenames[0])
            return filenames
        
    #Will add one file to the global image list
    def openFile(self, add_to_existing_list = False):
        file_list = self.openFileDialogue(folder_mode=False)
        if(file_list != None):
            if add_to_existing_list:
                self.globalImageList.append(file_list[0])
            else:
                self.globalImageList.clear() #flushing current list
                self.globalImageList.append(file_list[0])
                
        else:
            message = "No Image was selected"
            title = "Error :'("
            messages.display_message(message, title, messages.ERROR_MSG)
    
    def openFolder(self, add_to_existing_list = False):
        folder = self.openFileDialogue()
        
        if(folder != None):
            message = "Sort image list automatically?"
            result = messages.display_option_message(message, "Sort Do I?")
            if result == True: ## sorted images
                if add_to_existing_list:
                    self.globalImageList = self.globalImageList + generate_image_list(folder[0])
                       
                else:
                    self.isInFolderMode = True
                    self.folder = folder[0]
                    self.globalImageList.clear()
                    self.globalImageList = generate_image_list(folder[0])
                
            else: #unsorted images
                if add_to_existing_list:
                    self.globalImageList.append(generate_image_list(folder[0], sort_pictures=False))
                else:
                    self.isInFolderMode = True
                    self.folder = folder[0]
                    self.globalImageList = generate_image_list(folder[0],sort_pictures=False)
        else:
            message = "No folder was selected"
            title = "Error :'("
            messages.display_message(message, title, messages.ERROR_MSG)
    
    def saveFileDialog(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)
        if dialog.exec():
            filename = dialog.selectedFiles()
            if(len(filename) != 0):
                return (filename[0] + ".pdf")
            else:
                messages.display_message("No file name specified", "did you forgor", messages.ERROR_MSG)
        else:
            messages.display_message("Operation canceled", ":(", messages.ERROR_MSG)
    
    def addImagesToListView(self):
        imageModel = QStandardItemModel()
        for imagePath in self.globalImageList:
            item = QStandardItem()
            item.setIcon(QIcon(imagePath))
            #item.setBackground(QColor("#2e2e2e"))  # Dark background
            #item.setForeground(QColor("#ffffff"))  # Text color
            item.setText(imagePath)
            item.setData(imagePath)
            imageModel.appendRow(item)
            
        self.tblImagesList.setModel(imageModel)
        
    def getImages(self):
        imagesToBeSavedList = []
        imageModelFromQlistView = self.tblImagesList.model()
        for row in range(imageModelFromQlistView.rowCount()):
            item = imageModelFromQlistView.item(row)
            imageFilePath = item.text()
            imagesToBeSavedList.append(imageFilePath)
        
        return imagesToBeSavedList
    
    def batch_Mode_function(self):
        dialog = QtWidgets.QFileDialog(self)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        if dialog.exec():
            sourceFolder = dialog.selectedFiles()[0] # source folder
            folders = [f for f in os.listdir(sourceFolder) if os.path.isdir(os.path.join(sourceFolder, f))]
            outputFolder = sourceFolder + "\\output"
            create_folder(outputFolder)
            originalProgressLabelText = self.lblBatchModeProgress.text()
            totalFolders = len(folders)
            foldersDone = 0
            for folder in folders:
                self.lblBatchModeProgress.setText(f"{originalProgressLabelText}: ({foldersDone}/{totalFolders})")
                currentDirectory = f"{sourceFolder}\\{folder}" # we are getting the images here
                images = generate_image_list(currentDirectory)
                outputfilename = create_output_file_name(folder)
                print(outputfilename)
                convert_multiple_images_with_specified_file_path(images, f"{outputFolder}/{outputfilename}.pdf")
                foldersDone+=1
            title = "Batch Report"
            message = f"Job done. check the {outputFolder} directory for your files"
            messages.display_message(message=message, title=title, message_type=messages.INFO_MSG)
        
        
def launch():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ConvertorUI()
    app.exec()
    
if __name__ == "__main__":
    launch()