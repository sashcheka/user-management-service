# from io import BytesIO
#
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from src.core.db_helper import db_helper
# import pytest
# from httpx import AsyncClient
#
# from src.main import app
#
#
# @pytest.mark.asyncio
# @pytest.mark.e2e
# async def test_user_workflow(client: AsyncClient):
#     # Step 1: Sign up
#     signup_response = await client.post("/auth/signup/", data={...}, files={...})
#     assert signup_response.status_code == 200
#
#     # Extract user details as needed, for example:
#     user_details = signup_response.json()
#
#     # Step 2: Login
#     login_response = await client.post("/auth/login/", data={...})
#     assert login_response.status_code == 200
#
#     # Step 3: Update user data
#     update_response = await client.put("/user/update/", headers={...}, json={...})
#     assert update_response.status_code == 200
#
#     # Step 4: Delete user
#     delete_response = await client.delete(f"/user/{user_details['id']}/", headers={...})
#     assert delete_response.status_code == 200
