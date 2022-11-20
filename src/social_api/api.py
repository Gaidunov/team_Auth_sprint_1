from src.social_api.vk import vk_api


class SocialApi:
    """это интерфейс, в котором собираются апи всех сервисов"""

    def __init__(self) -> None:
        self.vk = vk_api


social_api = SocialApi()
