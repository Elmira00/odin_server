import requests

def get_user_email(user_id):
    if user_id:
        response = requests.get(f"https://api.example.com/users/{user_id}")
        if response.status_code == 200:
            user_data = response.json()
            return user_data.get('email')
        else:
            return None
    else:
        return None