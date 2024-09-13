import requests
class LineController : 
    def __init__ (self):
        self.token = 'SoSVUxGYfaM60NHE2enI2GpNCTxEHFYRxR53vFL1zNe'
        self.url = 'https://notify-api.line.me/api/notify'
        self.headers = {'Authorization': 'Bearer ' + self.token}
        self._lineNotify
        self.notifyPicture

    # file_path = r'C:\Users\s6204062660081\Desktop\lineNotify\picture\1.jpg'
    #main for line notify
    def _lineNotify(self , payload, file=None):
        try:
            return requests.post(self.url, headers=self.headers , data=payload, files=file)
        except Exception as e :
            print(e)

    def lineNotify(self , message):
        payload = {'message': message}
        return self._lineNotify(payload)

    def notifyPicture(self,file_path ,msg ):
        try:
            with open(file_path, 'rb') as file:
                files = {'imageFile': file}
                payload = {'message': msg}
                return self._lineNotify(payload, files)
        except Exception as e:
            print(f"Error opening file: {e}")
            return None

    def msgWithPic(self,message, file_path):
        print(f"Attempting to send message: {message} with picture at: {file_path}")
        self.lineNotify(message)
        notify_resultPic = self.notifyPicture(file_path)
        if notify_resultPic is None:
            print("Failed to send picture.")
            self.lineNotify("Failed to send picture from local storage in raspberry pie!")
        if(notify_resultPic):
            print("Send picture success.")

    # msgWithPic(message, file_path)