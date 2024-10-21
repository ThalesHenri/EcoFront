#this is a class that will hand sending the information for the form to an api
#made by tEaGaH
import requests
class ApiSender:
    def __init__(self,url):
        self.url = url
        self.formData = {'nome': 'Cerveja Latinha', 'marca': 'Heineken', 'peso': '1.04', 'quantidade': 5, 'frete': 'FOB', 'preco': '13.20', 'imagem': '/images_JzW5yb9.jpeg'}
        
    def addFormData(self,key,value):
        self.formData[key] = value
        
    def sendPostRequest(self):
        response = requests.post(self.url, data=self.formData)
        
        if response.status_code == 200:
            print("Form data submitted successfully.")
            try:
                print("Response:", response.json())
            except ValueError:
                print("Response:", response.text)
        else:
            print("Failed to submit form data.")
            print("Status code:", response.status_code)
            print("Response:", response.text)

    def sendGetRequest(self):
        response = requests.get(self.url)
        json = response.json()
        print(json)
        
apiSender = ApiSender('http://127.0.0.1:8081/api/produto/')
apiSender.sendPostRequest()
