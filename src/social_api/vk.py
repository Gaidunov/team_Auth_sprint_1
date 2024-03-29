import requests

import backoff
from pydantic.error_wrappers import ValidationError

from src.social_api.models import VkAccessResponse
from src.config import vk_settings

class VkApi:
 
    @backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException)
    def get_access_token(self, code:str)->VkAccessResponse: 
        url = 'https://oauth.vk.com/access_token'
        params = vk_settings.dict()
        params.update({'code':code})    
        vk_data = requests.get(url, params=params).json()
        try:
            vk_data = VkAccessResponse(**vk_data)
            return vk_data
        except ValidationError:
            print('не получается залогиниться ВК')
            
        
vk_api = VkApi()