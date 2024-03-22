import os
import requests
import logging

logger = logging.getLogger()


class SECOApi:

    URL = os.environ.get('SECO_API_URL', '')
    ACCESS_TOKEN = os.environ.get('SECO_API_ACCESS_TOKEN', '')

    WORKSPACE_STATE_STARTING = 1
    WORKSPACE_STATE_RUNNING = 2
    WORKSPACE_STATE_STOPPED = 3
    WORKSPACE_STATE_REMOVED = 4
    WORKSPACE_STATE_ERROR = 5

    class APIError(Exception):
        pass
    
    @classmethod
    def get_workspace(cls, workspace_id: str) -> dict:
        headers = {
            'Authorization': f'Bearer {cls.ACCESS_TOKEN}',
        }
        
        try:
            response = requests.get(f'{cls.URL}/workspaces/{workspace_id}', headers=headers)
            response.raise_for_status()
        except requests.HTTPError as e:
            try:
                desc = e.response.json()
            except:
                desc = str(e)
            raise cls.APIError(desc)
        except:
            # TODO Handle other exceptions 
            raise
        return response.json()

    @classmethod
    def create_workspace(cls, project_id: str, auto_resume: bool = None, workspace_token_required: bool = None, 
                         inactivity_timeout: int = None, retention_time_stopped: int = None, 
                         retention_time_total: int = None) -> dict:
        data = {
            'project_id': project_id,
            'auto_resume': auto_resume,
            'workspace_token_required': workspace_token_required,
            'inactivity_timeout': inactivity_timeout,
            'retention_time_stopped': retention_time_stopped,
            'retention_time_total': retention_time_total,
        }

        headers = {
            'Authorization': f'Bearer {cls.ACCESS_TOKEN}',
        }

        try:
            response = requests.post(f'{cls.URL}/workspaces', json=data, headers=headers)
            response.raise_for_status()
        except requests.HTTPError as e:
            try:
                desc = e.response.json()
            except:
                desc = str(e)
            raise cls.APIError(desc)
        except:
            # TODO Handle other exceptions 
            raise
        return response.json()
    
    @classmethod
    def resume_workspace(cls, workspace_id: str) -> dict:
        headers = {
            'Authorization': f'Bearer {cls.ACCESS_TOKEN}',
        }
        
        try:
            response = requests.put(f'{cls.URL}/workspaces/{workspace_id}/resume', headers=headers)
            response.raise_for_status()
        except requests.HTTPError as e:
            try:
                desc = e.response.json()
            except:
                desc = str(e)
            raise cls.APIError(desc)
        except:
            # TODO Handle other exceptions 
            raise
        return response.json()
