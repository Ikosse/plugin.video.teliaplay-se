import platform
import uuid
from resources.lib.webutils import WebUtils


class TeliaException(Exception):
    pass


def error_check(response_json):
    if "errors" in response_json:
        try:
            error_msg = response_json["errors"]["message"]
        except Exception:
            try:
                error_msg = response_json["errors"][0]["extensions"]["code"]
            except Exception:
                error_msg = response_json["errors"][0]["message"]
        raise TeliaException(error_msg)
    elif "errorMessage" in response_json:
        raise TeliaException(response_json["errorMessage"])
    elif "errorCode" in response_json:
        raise TeliaException(response_json["message"])


class TeliaPlay():

    def __init__(self, userdata):
        self.tv_client_boot_id = userdata["bootUUID"]
        self.device_id = userdata["deviceUUID"]
        self.session_id = str(uuid.uuid4())
        try:
            self.token_data = userdata["tokenData"]
        except KeyError:
            self.token_data = None
        self.web_utils = WebUtils()

    def login(self, username, password):
        request = {
            "POST": {
                "scheme": "https",
                "host": "ottapi.prod.telia.net",
                "filename": "/web/se/logingateway/rest/v1/login"
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "tv-client-boot-id": self.tv_client_boot_id
        }
        payload = {
            "deviceId": self.device_id,
            "username": username,
            "password": password,
            "deviceType": "WEB",
            "whiteLabelBrand": "TELIA"
        }

        response_json = self.web_utils.make_request(
            request, headers=headers, payload=payload
        ).json()
        error_check(response_json)
        self.token_data = response_json
        return response_json

    def validate_login(self):
        request = {
            "POST": {
                "scheme": "https",
                "host": "ottapi.prod.telia.net",
                "filename": "/web/se/tvclientgateway/rest/secure/v1/provision"
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }
        payload = {
            "deviceId": self.device_id,
            "uiVersion": "100e633",
            "nativeVersion": "N/A",
            "coreVersion": "7.0.4",
            "uiName": "telia-web",
            "platformName": platform.system()
        }
        response = self.web_utils.make_request(
            request, headers=headers, payload=payload
        )
        if response.status_code != 200:
            self.logout()
            error_check(response.json())

    def logout(self):
        request = {
            "DELETE": {
                "scheme": "https",
                "host": "ottapi.prod.telia.net",
                "filename": "/web/se/logingateway/rest/secure/v1/logout"
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "tv-client-boot-id": self.tv_client_boot_id
        }
        self.web_utils.make_request(
            request, headers=headers
        )

    def refresh_token(self):
        request = {
            "POST": {
                "scheme": "https",
                "host": "ottapi.prod.telia.net",
                "filename": "/web/se/logingateway/rest/v1/login/refresh"
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "tv-client-boot-id": self.tv_client_boot_id
        }
        payload = {
            "deviceId": self.device_id,
            "deviceType": "WEB",
            "refreshToken": self.token_data["refreshToken"]
        }

        response_json = self.web_utils.make_request(
            request, headers=headers, payload=payload
        ).json()
        error_check(response_json)
        self.token_data = response_json
        return response_json

    def get_main_menu(self):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "getMainMenu",
                    "variables": {},
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "3a18959010d36f5d47e7341167a2c596c11bdd2697bfb6ca7821862b048ff832"
                        }
                    }
                }
            }
        }

        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }

        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["mainMenu"]["items"]

    def search(self, query, limit, offset):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "search",
                    "variables": {
                        "q": query,
                        "limit": limit,
                        "offset": offset,
                        "searchRentalsType": "ALL"
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "958b924205529891e53b7000269afbbc63d27c171fbb569baae9c3466a681e32"
                        }
                    }
                }
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }
        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["search2"]

    def get_page(self, page_id):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "getPage",
                    "variables": {
                        "id": page_id
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "a1ae97411ecf06242ecc471813b409c6343358f712893afd1a5f0eb3ac267ac3"
                        }
                    }
                }
            }
        }

        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }

        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["page"]["pagePanels"]["items"]

    def get_channels(self, timestamp, program_limit=3):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "getTvChannels",
                    "variables": {
                        "timestamp": int(timestamp),
                        "limit": 20,
                        "programLimit": program_limit,
                        "offset": 0
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "c67f47ed145a5cd7700f403e60ac96b6213c71e9bfe4549b44685406b5b63c04"
                        }
                    }
                }
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }

        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["channels"]["channelItems"]

    def get_channel(self, channel_id, timestamp):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "getTvChannel",
                    "variables": {
                        "timestamp": timestamp,
                        "offset": 0,
                        "id": channel_id
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "50d41fa13c31529baba7f796dafa99418f2448024ffe91953d7961fb4b8ea011"
                        }
                    }
                }
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }

        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["channel"]

    def get_play_stores(self):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "getPage",
                    "variables": {
                        "id": "all-stores"
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "a1ae97411ecf06242ecc471813b409c6343358f712893afd1a5f0eb3ac267ac3"
                        }
                    }
                }
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }

        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["page"]["pagePanels"]["items"]

    def get_store(self, store_id):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "getStorePage",
                    "variables": {
                        "id": store_id,
                        "offset": 0
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "22d434cd12ff38bb4ae5fd1940b797706216c0b7ca76c86110e8b07b2955c658"
                        }
                    }
                }
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }

        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["store"]

    def get_panel(self, panel_id, limit, offset):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "getPanel",
                    "variables": {
                        "id": panel_id,
                        "config": {
                            "limit": limit,
                            "offset": offset,
                            "sort": {
                                "key": "TITLE",
                                "order": "ASC"
                            }
                        }
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "07ac910ce5dbad6dcd012598dc0b31b551dd2b1c6eaf8cb1972233fdef694249"
                        }
                    }
                }
            }
        }

        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }

        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["panel"]["selectionMediaContent"]

    def get_movie(self, movie_id):
        pass

    def get_series(self, series_id):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName":
                    "getSeries",
                    "variables": {
                        "id": series_id
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "52ad822a64944086e32b3de24f0474cf9dd8a69326c6029d3d9cc1e5e95a392d"
                        }
                    }
                }
            }
        }

        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }
        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["series"]

    def get_season(self, season_id):
        request = {
            "GET": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql",
                "query": {
                    "operationName": "getSeason",
                    "variables": {
                        "seasonId": season_id,
                        "sort": {
                            "order": "DESC"
                        }
                    },
                    "extensions": {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "fed3ca9ece5a7ddc4e0b0f4ab2fa0af261993aa7361730abb69431d2a43ce085"
                        }
                    }
                }
            }
        }

        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }

        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        return response_json["data"]["season"]["episodes"]["episodeItems"]

    def validate_stream(self):
        request = {
            "POST": {
                "scheme": "https",
                "host": "tvclientgateway-telia.clientapi-prod.live.tv.telia.net",
                "filename": "/tvclientgateway/rest/secure/v1/provision"
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
            "X-Configuration": "web",
            "X-Country": "se"
        }
        payload = {
            "deviceId": self.device_id,
            "drmType": "WIDEVINE",
            "category": "desktop_" + platform.system()
        }

        response = self.web_utils.make_request(
            request, headers=headers, payload=payload
        )
        if response.status_code != 200:
            error_check(response.json())

    def get_vod(self, video_id):
        request = {
            "GET": {
                "scheme": "https",
                "host": "ottapi.prod.telia.net",
                "filename": "/web/se/exploregateway/rest/v4/explore/media/{0}".format(video_id),
                "query": {
                    "deviceType": "WEB",
                    "protocols": "DASH"
                }
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
        }
        response_json = self.web_utils.make_request(
            request, headers=headers
        ).json()
        error_check(response_json)
        vods = response_json[video_id]["assets"]["vod"]
        for vod in vods:
            if vod["type"] == "TVOD" and vod["deviceType"] == "WEB":
                return vod
        return None

    def rent_video(self, vod_id, pin_code):
        request = {
            "POST": {
                "scheme": "https",
                "host": "atvse.telia.net",
                "filename": "/rest/v1/secure_v2/mediarentals/videos/{0}".format(vod_id)
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }
        payload = {
            "deviceType": "WEB",
            "purchasePinCode": pin_code
        }
        response_json = self.web_utils.make_request(
            request, headers=headers, payload=payload
        ).json()
        error_check(response_json)
        return response_json

    def add_to_my_list(self, media_id):
        request = {
            "POST": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql"
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"]
        }
        payload = {
            "operationName": "addToMyList",
            "variables": {
                "id": media_id,
                "type": "SERIES" if media_id.startswith("s") else "MEDIA"
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "70a1b84e1976a3b9773b25b9096e4e6c39128218720b5a6d2ccc0a0dd522919b"
                }
            }
        }
        response_json = self.web_utils.make_request(
            request, headers=headers, payload=payload
        ).json()
        error_check(response_json)
        return response_json

    def remove_from_my_list(self, media_id):
        request = {
            "POST": {
                "scheme": "https",
                "host": "graphql-telia.t6a.net",
                "filename": "/graphql"
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"]
        }
        payload = {
            "operationName": "removeFromMyList",
            "variables": {
                "id": media_id,
                "type": "SERIES" if media_id.startswith("s") else "MEDIA"
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "f1b3ae838fa9b39cc8c1994ff03039aaa09b494673bcaa3f49c04a17a5fa92a1"
                }
            }
        }
        response_json = self.web_utils.make_request(
            request, headers=headers, payload=payload
        ).json()
        error_check(response_json)
        return response_json

    def get_stream(self, stream_id, stream_type):
        request = {
            "POST": {
                "scheme": "https",
                "host": "streaminggateway-telia.clientapi-prod.live.tv.telia.net",
                "filename": "/streaminggateway/rest/secure/v2/streamingticket/"
                "{0}/{1}".format(
                    "CHANNEL" if stream_type == "live" else "MEDIA", stream_id),
                "query": {
                    "country": "SE"
                }
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
            "X-Country": "se"
        }
        payload = {
            "sessionId": self.session_id,
            "whiteLabelBrand": "TELIA",
            "watchMode": "LIVE" if stream_type == "live" else "ONDEMAND" if
            stream_type == "rental" else "TRAILER" if stream_type == "trailer" else "STARTOVER",
            "accessControl": "TRANSACTION" if stream_type == "rental" else "SUBSCRIPTION",
            "device": {
                "deviceId": self.device_id,
                "packagings": ["DASH_MP4_CTR"],
                "drmType": "WIDEVINE",
                "capabilities": [],
                "screen": {"height": 1080, "width": 1920},
                "os": platform.system()
            },
            "preferences": {
                "audioLanguage": ["undefined"],
                "accessibility": []
            }
        }

        response_json = self.web_utils.make_request(
            request, headers=headers, payload=payload
        ).json()
        error_check(response_json)

        if stream_type == "live":
            return response_json["streams"][1]
        else:
            return response_json["streams"][0]

    def delete_stream(self):
        request = {
            "DELETE": {
                "scheme": "https",
                "host": "streaminggateway-telia.clientapi-prod.live.tv.telia.net",
                "filename": "/streaminggateway/rest/secure/v2/streamingticket/CHANNEL/18",
                "query": {
                    "sessionId": self.session_id,
                    "whiteLabelBrand": "TELIA",
                    "country": "SE"
                }
            }
        }
        headers = {
            "User-Agent": "kodi.tv",
            "client-name": "web",
            "tv-client-boot-id": self.tv_client_boot_id,
            "Authorization": "Bearer " + self.token_data["accessToken"],
        }
        payload = {}
        response = self.web_utils.make_request(
            request, headers=headers, payload=payload
        )
        return response
