import base64, httpx
from lexica.constants import *
from lexica.utils import *
from typing import Union,Dict

class Client:
    """
    Sync Client
    """
    def __init__(
        self
    ):
        """
        Initialize the class
        """
        self.url = BASE_URL
        self.session = httpx.Client(
                http2=True
            )
        self.timeout = 60
        self.headers = SESSION_HEADERS
    
    def _request(self, **kwargs) -> Union[Dict,bytes]:
        self.headers.update(kwargs.get("headers",{}))
        contents = {'json':{},'data':{},'files':{}}
        for i in list(contents):
            if i in kwargs:
                contents[i] = clean_dict(kwargs.get(i))
        response = self.session.request(
                method=kwargs.get('method', 'GET'),
                url=kwargs.get('url'),
                headers=self.headers,
                params=kwargs.get('params'),
                data=contents.get('data'),
                json=contents.get('json'),
                files=contents.get('files'),
                timeout=self.timeout,
            )
        if response.status_code != 200:
            raise Exception(f"API error {response.text}")
        if response.headers.get('content-type') in ['image/png','image/jpeg','image/jpg'] :
            return response.content
        rdata = response.json()
        if rdata['code'] == 0:
            raise Exception(f"API error {response.text}")
        return rdata

    def getModels(self) -> dict:
        resp = self._request(url=f'{self.url}/models')
        return resp
    
    def palm(self, prompt: str) -> dict:
        """ 
        Get an answer from PaLM 2 for the given prompt
        Example:
        >>> client = Client()
        >>> response = client.palm("Hello, Who are you?")
        >>> print(response)

        Args:
            prompt (str): Input text for the query.

        Returns:
            dict: Answer from the API in the following format:
                {
                    "message": str,
                    "content": str,
                    "code": int
                }
        """
        params = {
            "model_id": 0,
            "prompt": prompt
        }
        resp = self._request(
            url=f'{self.url}/models',
            method='POST',
            params=params,
            headers = {"content-type": "application/json"}
        )
        return resp

    def gpt(self, prompt: str,context: str=False) -> dict:
        """ 
        Get an answer from GPT-3.5-Turbo for the given prompt
        Example:
        >>> client = Client()
        >>> response = client.gpt("Hello, Who are you?")
        >>> print(response)

        Args:
            prompt (str): Input text for the query.

        Returns:
            dict: Answer from the API in the following format:
                {
                    "status": str,
                    "content": str
                }
        """
        params = {
            "model_id": 5,
            "prompt": prompt
            ,"context": context if context else ''
        }
        resp = self._request(
            url=f'{self.url}/models',
            method='POST',
            params=params,
            headers={"content-type": "application/json"}
            )
        return resp

    def upscale(self, image: bytes) -> bytes:
        """ 
        Upscale an image
        Example:
        >>> client = Client()
        >>> response = client.upscale(image)
        >>> with open('upscaled.png', 'wb') as f:
                f.write(response)

        Args:
            image (bytes): Image in bytes.
        Returns:
            bytes: Upscaled image in bytes.
        """
        b = base64.b64encode(image).decode('utf-8')
        content = self._request(
            url=f'{self.url}/upscale',
            method = 'POST',
            json={'image_data': b}
        )
        return content

    def generate(self,model_id:int,prompt:str,negative_prompt:str="",images: int=1) -> dict:
        """ 
        Generate image from a prompt
        Example:
        >>> client = Client()
        >>> response = client.generate(model_id,prompt,negative_prompt)
        >>> print(response)

        Args:
            prompt (str): Input text for the query.
            negative_prompt (str): Input text for the query.

        Returns:
            dict: Answer from the API in the following format:
                {
                    "message": str,
                    "task_id": int,
                    "request_id": str
                }
        """
        payload = {
            "model_id": model_id,
            "prompt": prompt,
            "negative_prompt": negative_prompt, #optional
            "num_images": images,  #optional number of images to generate (default: 1) and max 4
        }
        resp = self._request(
            url=f'{self.url}/models/inference',
            method='POST',
            json=payload,
            headers={"content-type": "application/json"}
        )
        return resp
    
    def getImages(self,task_id:str,request_id:str) -> dict:
        """ 
        Generate image from a prompt
        Example:
        >>> client = Client()
        >>> response = client.getImages(task_id,request_id)
        >>> print(response)

        Args:
            prompt (str): Input text for the query.
            negative_prompt (str): Input text for the query.

        Returns:
            dict: Answer from the API in the following format:
                {
                    "message": str,
                    "img_urls": array,
                    "code": int
                }
        """
        payload = {
            "task_id": task_id,
            "request_id": request_id
        }
        resp = self._request(
            url=f'{self.url}/models/inference/task',
            method='POST',
            json=payload,
            headers={"content-type": "application/json"}
        )
        return resp