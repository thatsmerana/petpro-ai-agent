import asyncio
import json
from typing import Dict, List
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

class PetProfessionalsAPIClient:
    """Client for pet professionals APIs"""

    def __init__(self):
        self.base_url = os.getenv("PET_PROFESSIONALS_API_BASE_URL")
        self.api_key = os.getenv("PET_PROFESSIONALS_API_KEY")


    # Get existing customers profiles by pet professionals id
    async def get_customer_profiles_by_pet_professionals_id(self, pet_professionals_id: str) -> Dict:
        """Get existing customers profiles by pet professionals id"""
        url = f"{self.base_url}/api/v1/customers/professional/{pet_professionals_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    # Create new customer profile
    async def create_customer(self, customer_data: Dict) -> Dict:
        """Create new customer profile

        Args:
            customer_data: Complete customer object including:
                - firstName: Customer's first name
                - lastName: Customer's last name
                - email: Customer's email
                - phone: Customer's phone number
                - address: Customer's address
                - professionalId: Professional's UUID
                - pets: Optional list of pet objects
        """
        url = f"{self.base_url}/api/v1/customers"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"} if self.api_key else {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=customer_data) as response:
                response.raise_for_status()
                return await response.json()


    # Add new Pet profiles to existing customer
    async def create_pet_profiles(self, customer_data: Dict) -> Dict:
        """Add new Pet profiles to existing customer

        Args:
            customer_data: Complete customer object including:
                - id: Customer UUID
                - professionalId: Professional's UUID
                - pets: List of pet objects to add
                - Other customer fields
        """
        customer_id = customer_data.get("id")
        if not customer_id:
            raise ValueError("customer_data must include 'id' field")

        url = f"{self.base_url}/api/v1/customers/{customer_id}"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"} if self.api_key else {"Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=customer_data) as response:
                response.raise_for_status()
                return await response.json()

    # Get services by professional id
    async def get_services_by_professional_id(self, professional_id: str) -> Dict:
        """Get services information by professional id"""
        url = f"{self.base_url}/api/v1/services/professional/{professional_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

    # Create new booking
    async def create_booking(self, booking_data: Dict) -> Dict:
        """Create new booking

        Args:
            booking_data: Complete booking object including:
                - clientId: Customer UUID
                - serviceId: Service UUID
                - professionalId: Professional's UUID
                - startDate: Booking start date (YYYY-MM-DD)
                - endDate: Booking end date (YYYY-MM-DD)
                - startTime: Start time (HH:MM)
                - endTime: End time (HH:MM)
                - extraPetFee: Additional fee for extra pets
                - weekendFee: Weekend surcharge
                - notes: Booking notes
                - bookingPets: List of pet objects with petId and specialInstructions
        """
        url = f"{self.base_url}/api/v1/bookings"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"} if self.api_key else {"Content-Type": "application/json"}

        print(f"🔍 DEBUG - Booking URL: {url}")
        print(f"🔍 DEBUG - Booking Data: {json.dumps(booking_data, indent=2)}")

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=booking_data) as response:
                response_text = await response.text()
                print(f"🔍 DEBUG - Response Status: {response.status}")
                print(f"🔍 DEBUG - Response Text: {response_text}")

                if response.status >= 400:
                    raise Exception(f"API Error {response.status}: {response_text}")

                return await response.json() if response_text else {}
