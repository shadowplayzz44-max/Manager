import aiohttp
import asyncio
from typing import Optional, Dict, List, Any
import random
import string

class PterodactylAPI:
    def __init__(self, panel_url: str, app_key: str, client_key: str):
        self.panel_url = panel_url.rstrip('/')
        self.app_key = app_key
        self.client_key = client_key
        self.app_headers = {
            'Authorization': f'Bearer {app_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.client_headers = {
            'Authorization': f'Bearer {client_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    async def _request(self, method: str, endpoint: str, headers: dict, data: dict = None) -> Dict:
        """Make API request"""
        url = f"{self.panel_url}/api/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url, headers=headers, json=data) as resp:
                    if resp.status == 204:
                        return {'success': True}
                    
                    response_data = await resp.json()
                    
                    if resp.status >= 400:
                        error_msg = response_data.get('errors', [{}])[0].get('detail', 'Unknown error')
                        return {'success': False, 'error': error_msg, 'status': resp.status}
                    
                    return {'success': True, 'data': response_data}
            except aiohttp.ClientError as e:
                return {'success': False, 'error': f'Connection error: {str(e)}'}
            except Exception as e:
                return {'success': False, 'error': str(e)}
    
    # ==================== USER MANAGEMENT ====================
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        result = await self._request('GET', f'application/users?filter[email]={email}', self.app_headers)
        if result['success'] and result['data']['data']:
            return result['data']['data'][0]
        return None
    
    async def create_user(self, email: str, username: str, first_name: str, last_name: str) -> Dict:
        """Create a new user"""
        password = self._generate_password()
        
        data = {
            'email': email,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'password': password
        }
        
        result = await self._request('POST', 'application/users', self.app_headers, data)
        if result['success']:
            result['password'] = password
        return result
    
    async def list_users(self, page: int = 1) -> Dict:
        """List all users"""
        return await self._request('GET', f'application/users?page={page}', self.app_headers)
    
    async def delete_user(self, user_id: int) -> Dict:
        """Delete a user"""
        return await self._request('DELETE', f'application/users/{user_id}', self.app_headers)
    
    async def update_user_password(self, user_id: int, password: str) -> Dict:
        """Update user password"""
        data = {'password': password}
        return await self._request('PATCH', f'application/users/{user_id}', self.app_headers, data)
    
    # ==================== SERVER MANAGEMENT ====================
    
    async def create_server(self, user_id: int, name: str, ram: int, cpu: int, 
                           disk: int, node_id: int, egg_id: int, docker_image: str = None) -> Dict:
        """Create a new server"""
        
        # Get egg details to find default docker image
        if not docker_image:
            egg_result = await self.get_egg(egg_id)
            if egg_result['success']:
                docker_image = egg_result['data']['attributes']['docker_image']
            else:
                docker_image = 'ghcr.io/pterodactyl/yolks:java_17'
        
        data = {
            'name': name,
            'user': user_id,
            'egg': egg_id,
            'docker_image': docker_image,
            'startup': '',
            'environment': {},
            'limits': {
                'memory': ram,
                'swap': 0,
                'disk': disk,
                'io': 500,
                'cpu': cpu
            },
            'feature_limits': {
                'databases': 1,
                'allocations': 1,
                'backups': 2
            },
            'allocation': {
                'default': await self._get_first_available_allocation(node_id)
            }
        }
        
        return await self._request('POST', 'application/servers', self.app_headers, data)
    
    async def _get_first_available_allocation(self, node_id: int) -> int:
        """Get first available allocation for node"""
        result = await self._request('GET', f'application/nodes/{node_id}/allocations', self.app_headers)
        if result['success']:
            for alloc in result['data']['data']:
                if not alloc['attributes']['assigned']:
                    return alloc['attributes']['id']
        return 1  # Fallback
    
    async def list_servers(self, page: int = 1) -> Dict:
        """List all servers"""
        return await self._request('GET', f'application/servers?page={page}', self.app_headers)
    
    async def get_server(self, server_id: int) -> Dict:
        """Get server details"""
        return await self._request('GET', f'application/servers/{server_id}', self.app_headers)
    
    async def delete_server(self, server_id: int, force: bool = False) -> Dict:
        """Delete a server"""
        endpoint = f'application/servers/{server_id}'
        if force:
            endpoint += '/force'
        return await self._request('DELETE', endpoint, self.app_headers)
    
    async def suspend_server(self, server_id: int) -> Dict:
        """Suspend a server"""
        return await self._request('POST', f'application/servers/{server_id}/suspend', self.app_headers)
    
    async def unsuspend_server(self, server_id: int) -> Dict:
        """Unsuspend a server"""
        return await self._request('POST', f'application/servers/{server_id}/unsuspend', self.app_headers)
    
    async def update_server_build(self, server_id: int, ram: int = None, cpu: int = None, 
                                 disk: int = None) -> Dict:
        """Update server resource limits"""
        data = {
            'allocation': 1,  # Keep existing allocation
            'limits': {}
        }
        
        # Get current server details
        server = await self.get_server(server_id)
        if not server['success']:
            return server
        
        current_limits = server['data']['attributes']['limits']
        
        data['limits']['memory'] = ram if ram is not None else current_limits['memory']
        data['limits']['cpu'] = cpu if cpu is not None else current_limits['cpu']
        data['limits']['disk'] = disk if disk is not None else current_limits['disk']
        data['limits']['swap'] = current_limits.get('swap', 0)
        data['limits']['io'] = current_limits.get('io', 500)
        
        return await self._request('PATCH', f'application/servers/{server_id}/build', self.app_headers, data)
    
    # ==================== NODE MANAGEMENT ====================
    
    async def list_nodes(self) -> Dict:
        """List all nodes"""
        return await self._request('GET', 'application/nodes', self.app_headers)
    
    async def get_node(self, node_id: int) -> Dict:
        """Get node details"""
        return await self._request('GET', f'application/nodes/{node_id}', self.app_headers)
    
    # ==================== EGG MANAGEMENT ====================
    
    async def list_eggs(self, nest_id: int = 1) -> Dict:
        """List all eggs in a nest"""
        return await self._request('GET', f'application/nests/{nest_id}/eggs', self.app_headers)
    
    async def get_egg(self, egg_id: int) -> Dict:
        """Get egg details"""
        # Note: Need to know nest_id, default to 1 (Minecraft)
        return await self._request('GET', f'application/nests/1/eggs/{egg_id}', self.app_headers)
    
    # ==================== CLIENT API (Power, Backups, etc) ====================
    
    async def get_server_resources(self, server_uuid: str) -> Dict:
        """Get server resource usage (Client API)"""
        return await self._request('GET', f'client/servers/{server_uuid}/resources', self.client_headers)
    
    async def list_backups(self, server_uuid: str) -> Dict:
        """List server backups"""
        return await self._request('GET', f'client/servers/{server_uuid}/backups', self.client_headers)
    
    async def create_backup(self, server_uuid: str) -> Dict:
        """Create server backup"""
        return await self._request('POST', f'client/servers/{server_uuid}/backups', self.client_headers)
    
    # ==================== UTILITY ====================
    
    def _generate_password(self, length: int = 16) -> str:
        """Generate random password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))
    
    async def test_connection(self) -> bool:
        """Test API connection"""
        result = await self._request('GET', 'application/users?page=1', self.app_headers)
        return result['success']
