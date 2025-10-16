import img2pdf as im
import PIL
import os, sys
from PyQt6.QtCore import QSize
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QAbstractItemView
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QColor
import messages

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

#sorts by default
def generate_image_list(images_dir_folder, sort_pictures=True):
    images = []
    for fname in os.listdir(images_dir_folder):
        if not fname.endswith((".jpg", ".png", ".jpeg")):
            continue
        
        path = os.path.join(images_dir_folder, fname)
        if(os.path.isdir(path)):
            continue
        images.append(path)
    if sort_pictures == True:
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
    

class ConvertorUI(QtWidgets.QMainWindow):
    globalImageList = []
    defaultFileDirectoryText =  None
    globalImageModel = None #this is for the qListView 
    
    def __init__(self):
        super(ConvertorUI, self).__init__()
        uic.loadUi("convertorUI.ui", self)
        self.show()
        self.defaultFileDirectoryText = self.lblFileDirectory.text()
        #Image models
        self.globalImageModel = QStandardItemModel()
        self.tblImagesList.setFlow(QtWidgets.QListView.Flow.TopToBottom)
        self.tblImagesList.setMovement(QtWidgets.QListView.Movement.Snap)
        self.tblImagesList.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        self.tblImagesList.setGridSize(QSize(120, 120))
        self.tblImagesList.setIconSize(QSize(120,120))
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
    
    def addImage(self):
          self.openFile(add_to_existing_list=True)
              
    def addFolder(self):
        self.openFolder(add_to_existing_list=True)
    
    def openImage(self):
        self.openFile(add_to_existing_list=False)
    
    def btnOpenFolderFunction(self):
        self.openFolder(add_to_existing_list=False)
        self.addImagesToListView()
        
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
                    self.globalImageList.clear()
                    self.globalImageList = generate_image_list(folder[0])
                
            else: #unsorted images
                if add_to_existing_list:
                    self.globalImageList.append(generate_image_list(sort_pictures=False))
                else:    
                    self.globalImageList = generate_image_list(sort_pictures=False)
        else:
            message = "No folder was selected"
            title = "Error :'("
            messages.display_message(message, title, messages.ERROR_MSG)
    
    def addImagesToListView(self):
        for imagePath in self.globalImageList:
            item = QStandardItem()
            item.setIcon(QIcon(imagePath))
            item.setBackground(QColor("#2e2e2e"))  # Dark background
            item.setForeground(QColor("#ffffff"))  # Text color
            item.setText(imagePath)
            self.globalImageModel.appendRow(item)
            
        self.tblImagesList.setModel(self.globalImageModel)
        
def launch():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ConvertorUI()
    app.exec()
    
if __name__ == "__main__":
    launch()