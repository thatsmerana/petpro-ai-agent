from typing import Dict
from .api_client import PetProfessionalsAPIClient
import json

# Initialize the API client
api_client = PetProfessionalsAPIClient()

async def get_customer_profile(pet_professional_id: str) -> str:
    """Get existing customers profiles by pet professionals id

    Args:
        pet_professional_id: ID of the pet professionals (Pet sitter, Dog walker, etc.)

    Returns:
        JSON string with success status and customer profile data. The data contains a list of customer objects, each with:
            - id: Customer UUID
            - createdAt: Timestamp of creation
            - updatedAt: Timestamp of last update
            - firstName: Customer's first name
            - lastName: Customer's last name
            - email: Customer's email address
            - phone: Customer's phone number
            - address: Customer's physical address
            - professionalId: Professional's UUID
            - pets: List of pet objects belonging to this customer, each pet has:
                - id: Pet UUID
                - createdAt: Timestamp of pet creation
                - updatedAt: Timestamp of last update
                - ownerId: Customer UUID (owner of the pet)
                - name: Pet's name
                - species: Pet species (e.g., "Dog", "Cat")
                - breed: Pet breed (e.g., "Golden Retriever", "Persian")
                - dateOfBirth: Birth date (YYYY-MM-DD format)
                - gender: Pet gender ("Male", "Female")
                - notes: Additional notes about the pet
                - color: Pet's color (e.g., "Golden", "Tabby", "Brown")
                - microchipNumber: Microchip identification number (may be empty string)
                - neutered: Boolean indicating if pet is neutered/spayed
                - vaccinations: Vaccination history as string (e.g., "Rabies: 2023-01-15, DHPP: 2023-02-01")
                - primaryVetId: Primary veterinarian UUID (may be null)
                - primaryVetName: Primary veterinarian's name (may be null)
                - primaryVetClinic: Primary vet clinic name (may be null)
                - alternateVetId: Alternate veterinarian UUID (may be null)
                - alternateVetName: Alternate veterinarian's name (may be null)
                - alternateVetClinic: Alternate vet clinic name (may be null)
                - imageUrl: URL to pet's photo (may be empty string)
                - active: Boolean indicating if pet profile is active
    """
    try:
        result = await api_client.get_customer_profiles_by_pet_professionals_id(pet_professional_id)
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def create_customer(customer_data_json: str) -> str:
    """Create new customer profile

    Args:
        customer_data_json: JSON string of customer object including:
            - firstName: Customer's first name
            - lastName: Customer's last name
            - email: Customer's email
            - phone: Customer's phone number
            - address: Customer's address
            - professionalId: Professional's UUID
            - pets: Optional list of pet objects, each pet should have:
                - ownerId: Customer UUID
                - name: Pet's name
                - species: Pet species (e.g., "Dog", "Cat")
                - breed: Pet breed
                - dateOfBirth: Birth date (YYYY-MM-DD format)
                - gender: Pet gender ("Male", "Female")
                - notes: Additional notes about the pet
                - isActive: Boolean indicating if pet profile is active
                - color: Pet's color
                - microchipNumber: Microchip identification number
                - neutered: Boolean indicating if pet is neutered/spayed
                - vaccinations: Vaccination history as string
                - imageUrl: URL to pet's photo

    Returns:
        JSON string with created customer information and success status
    """
    try:
        customer_data = json.loads(customer_data_json)
        result = await api_client.create_customer(customer_data)
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def create_pet_profiles(customer_data_json: str) -> str:
    """Add new pet profiles to existing customer

    Args:
        customer_data_json: JSON string of customer object including:
            - id: Customer UUID
            - professionalId: Professional's UUID
            - pets: List of pet objects to add, each pet should have:
                - ownerId: Customer UUID
                - name: Pet's name
                - species: Pet species (e.g., "Dog", "Cat")
                - breed: Pet breed
                - dateOfBirth: Birth date (YYYY-MM-DD format)
                - gender: Pet gender ("Male", "Female")
                - notes: Additional notes about the pet
                - isActive: Boolean indicating if pet profile is active
                - color: Pet's color
                - microchipNumber: Microchip identification number
                - neutered: Boolean indicating if pet is neutered/spayed
                - vaccinations: Vaccination history as string
                - imageUrl: URL to pet's photo
            - Other customer fields (firstName, lastName, email, phone, address)

    Returns:
        JSON string with updated customer information and success status
    """
    try:
        customer_data = json.loads(customer_data_json)
        result = await api_client.create_pet_profiles(customer_data)
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def get_services(professional_id: str) -> str:
    """Get services information by professional id

    Args:
        professional_id: ID of the pet professional

    Returns:
        JSON string with services information and success status. The data contains a list of service objects, each with:
            - id: Service UUID
            - createdAt: Timestamp of creation
            - updatedAt: Timestamp of last update
            - name: Service name (e.g., "Dog Walking", "Pet Grooming")
            - description: Service description
            - notes: Public notes about the service
            - internalNotes: Internal notes (may be null)
            - taxesEnabled: Boolean indicating if taxes are enabled
            - amount: Service base amount (may be null)
            - duration: Duration value (integer)
            - durationType: Duration type (e.g., "MINUTES", "min", "minutes")
            - mobileCounter: Mobile counter value
            - mobileCounterType: Type of mobile counter (e.g., "PER_SERVICE", "min", "per_visit")
            - websiteVisible: Boolean indicating if visible on website
            - gpsTrackingEnabled: Boolean for GPS tracking
            - lateReminders: Late reminder setting (e.g., "15_MINUTES", "AfterServiceEnd")
            - autoStackFees: Boolean for automatic fee stacking
            - serviceAvailability: List of availability objects, each with:
                - day: Day of week (e.g., "Monday")
                - timeBlock: Time range (e.g., "09:00:00-10:00:00" or "09:00-12:00")
                - timeBlockName: Name of time block (e.g., "Morning", may be null)
                - serviceId: Service UUID (may be null)
            - serviceRate: Object containing pricing information:
                - id: Rate UUID (may be null)
                - createdAt: Timestamp (may be null)
                - updatedAt: Timestamp (may be null)
                - serviceId: Service UUID
                - amount: Base service amount (may be null)
                - currency: Currency code (e.g., "USD")
                - extraPets: Object with onePetAmount and onePlusPetAmount (may be null)
                - afterHours: Object with amount, chargeType, startTime, endTime, status (may be null)
                - weekends: Object with chargeType, amount, customized, weekends array, status (may be null)
                - holidays: Object with chargeType and amount (may be null)
            - serviceDiscounts: List of discount objects, each with:
                - id: Discount UUID
                - serviceId: Service UUID
                - discountCode: Object with id, code, description, discountType, discountValue, etc.
                - minBookings: Minimum bookings required
                - frequencyType: Frequency type (e.g., "weekly")
                - enabled: Boolean indicating if discount is enabled
            - professionalId: Professional's UUID
            - active: Boolean indicating if service is active
            - archived: Boolean indicating if service is archived
    """
    try:
        result = await api_client.get_services_by_professional_id(professional_id)
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def create_booking(booking_data_json: str) -> str:
    """Create new booking

    Args:
        booking_data_json: JSON string of booking object including:
            - clientId: Customer UUID
            - serviceId: Service UUID
            - professionalId: Professional's UUID
            - startDate: Booking start date (YYYY-MM-DD)
            - endDate: Booking end date (YYYY-MM-DD)
            - startTime: Start time (HH:MM)
            - endTime: End time (HH:MM)
            - extraPetFee: Additional fee for extra pets (decimal number)
            - weekendFee: Weekend surcharge (decimal number)
            - notes: Booking notes
            - bookingPets: List of pet objects for this booking, each should have:
                - petId: Pet UUID
                - specialInstructions: Special instructions for this pet during booking

    Returns:
        JSON string with created booking information and success status
    """
    try:
        booking_data = json.loads(booking_data_json)
        result = await api_client.create_booking(booking_data)
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })
