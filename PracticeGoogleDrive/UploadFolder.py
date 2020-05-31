from __future__ import print_function
import os
import io
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): os.getcwd()

# 權限必須
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

def createFolder(service, folder_name, parent=None):
    """
    當要尋找的資料夾不存在時，建立資料夾
    :param service: 認證用
    :param folder_name: 要建立的資料夾
    :param parent: 是否要放在特定目錄下
    """
    folder_metadata = {
                        'name': folder_name,
                        # Define the file type as folder
                        'mimeType': 'application/vnd.google-apps.folder',
                        }
    # ID of the parent folder
    if parent != None: folder_metadata.update({'parents': [parent]})
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    print(f'Created Folder : {folder_name}, id : {folder["id"]}, parent : {parent}')
    return folder['id']

def _searchFolder(service, parent_id, target_name):
    """
    資料夾須逐層尋找，所以有一個被保護的方法來向下尋找目標資料夾
    """
    children = service.files().list(q=f"'{parent_id}' in parents").execute()
    target = None
    for child in children.get('files',[]):
        if child['mimeType'] == 'application/vnd.google-apps.folder' and child['name'] == target_name:
            print(f"Exist Folder : {child['name']}, id : {child['id']}")
            target = child#.get('id', '')
    # 如果找到的資料夾在垃圾桶裡面
    if _isTrashed(service, target, deleteIt=True): target = None #return createFolder(service, target_name, parent_id)
    # 如果資料夾不存在
    if target is None: return createFolder(service, target_name, parent_id)
    return target.get('id', '')

def searchFolder(service, destinationFolderName, parentsFolderList):
    """
    尋找資料夾
    """
    # Call the Drive v3 API
    results = service.files().list(fields="nextPageToken, files(id, name)", spaces='drive',
                                   q="name = '" + parentsFolderList[0] + "' and trashed = false",
                                   ).execute()
    items = results.get('files', [])
    if not items: return print('沒有發現你要找尋的 ' + parentsFolderList[0] + ' 檔案.')
    tempParent_Id = None
    for item in items:
        if item.get('name', '') == parentsFolderList[0]:
            print(f"Exist Folder : {item['name']}, id : {item['id']}")
            tempParent_Id = item.get('id', '')
    # no parent folder, create a new folder
    if tempParent_Id is None: tempParent_Id = createFolder(service, parentsFolderList[0])
    # 若已找到目標目錄，則返回資料夾的id
    if len(parentsFolderList[1:]) == 0: return tempParent_Id
    parent_id = None
    for parent in parentsFolderList[1:]:
        parent_id = _searchFolder(service, parent_id if parent_id != None else tempParent_Id, parent)
    return _searchFolder(service, parent_id if parent_id != None else tempParent_Id, destinationFolderName)

def checkingFileExist(service, folder_id, target):
    """
    確認子資料夾是否存在
    """
    children = service.files().list(q=f"'{folder_id}' in parents").execute()
    return any([target == child.get('name', '') for child in children.get('files',[])])

def _uploadFile(service, folder, fileForUpload):
    """
    上傳單一檔案
    """
    file_metadata = {'name': fileForUpload.replace(os.path.dirname(fileForUpload), '')[1:], 'parents': [folder]}
    media = MediaFileUpload(fileForUpload, )
    file_metadata_size = media.size()
    start_time = time.time()
    file_id = service.files().create(body=file_metadata, media_body=media, fields='id').execute() 
    duration = time.time() - start_time
    print("上傳檔案成功！")
    print('雲端檔案名稱為: ' + str(file_metadata['name']))
    print('雲端檔案ID為: ' + str(file_id['id']))
    print('檔案大小為: ' + str(file_metadata_size) + ' byte')
    print("上傳時間為: " + str(duration))

def UploadFiles(service, destinationFolderName, parentsFolderList, sourceDirectory):
    """
    上傳所有資料夾內的檔案
    """
    Folder_id = searchFolder(service, destinationFolderName, parentsFolderList)
    fileList = os.listdir(sourceDirectory)
    for f in fileList:
        if not checkingFileExist(service, Folder_id, f):
            _uploadFile(service, Folder_id, os.path.join(sourceDirectory, f))

def _isTrashed(service, target, deleteIt=False):
    """
    確定是否資料夾或檔案是否在垃圾桶裡
    """
    if target.get('id', '') in SearchTrashCan(service):
        if deleteIt: delete_drive_service_file(service, target=target)
        return True
    return False

def delete_drive_service_file(service, target):
    """
    刪除指定的 Folder/File
    """
    print(f'Delete File/Dir : {target.get("name","")}, id : {target.get("id", "")}')
    service.files().delete(fileId=target.get('id')).execute()

def SearchTrashCan(service, is_delete_trashed_file=False):
    """
    取得垃圾桶裡所有東西的id清單
    """
    results = service.files().list(fields="nextPageToken, files(id, name)", spaces='drive', q="trashed = true",
                                   ).execute()
    return [x.get('id', '') for x in results.get('files', [])]

def main():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(path, 'SelfCredentials.json'), SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    destinationFolderName = 'test'
    parentsFolderList = ['外包', '啟芳']
    sourceDirectory = os.path.join(path, 'test')
    UploadFiles(service, destinationFolderName, parentsFolderList, sourceDirectory)
    #SearchTrashCan(service)


if __name__ == "__main__":
    main()