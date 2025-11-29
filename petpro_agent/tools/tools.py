from .api_client import PetProfessionalsAPIClient
import json
import time
from typing import Dict, List, Any, Optional

try:
    from google.adk.tools.tool_context import ToolContext
except ImportError:
    # Fallback for when ToolContext is not available
    from typing import Any
    ToolContext = Any  # Type hint fallback

# Try to import rapidfuzz for fuzzy string matching, fallback to simple matching
try:
    from rapidfuzz import fuzz
    HAS_FUZZY_MATCHING = True
except ImportError:
    HAS_FUZZY_MATCHING = False

# Initialize the API client
api_client = PetProfessionalsAPIClient()


# Helper functions for extracting fields from API responses
def extract_customer_fields(customer_response: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract relevant fields from customer profile response.
    
    Args:
        customer_response: List of customer objects from API
        
    Returns:
        Dictionary with extracted fields:
        - customer_id: First customer ID if found
        - customers: Full list of customers
        - existing_pets: List of all pets from all customers
    """
    extracted = {
        "customer_id": None,
        "customers": customer_response if isinstance(customer_response, list) else [],
        "existing_pets": []
    }
    
    if isinstance(customer_response, list) and len(customer_response) > 0:
        # Get first customer ID (most common use case)
        first_customer = customer_response[0]
        if isinstance(first_customer, dict) and "id" in first_customer:
            extracted["customer_id"] = first_customer["id"]
        
        # Extract all pets from all customers
        for customer in customer_response:
            if isinstance(customer, dict) and "pets" in customer:
                pets = customer.get("pets", [])
                if isinstance(pets, list):
                    extracted["existing_pets"].extend(pets)
    
    return extracted


def extract_booking_fields(booking_response: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract relevant fields from bookings response.
    
    Args:
        booking_response: List of booking objects from API
        
    Returns:
        Dictionary with extracted fields:
        - booking_id: First booking ID if found
        - bookings: Full list of bookings
        - customer_ids: Set of unique customer IDs
        - pet_ids: Set of unique pet IDs from all bookings
    """
    extracted = {
        "booking_id": None,
        "bookings": booking_response if isinstance(booking_response, list) else [],
        "customer_ids": set(),
        "pet_ids": set()
    }
    
    if isinstance(booking_response, list) and len(booking_response) > 0:
        # Get first booking ID
        first_booking = booking_response[0]
        if isinstance(first_booking, dict) and "id" in first_booking:
            extracted["booking_id"] = first_booking["id"]
        
        # Extract customer IDs and pet IDs from all bookings
        for booking in booking_response:
            if isinstance(booking, dict):
                if "clientId" in booking and booking["clientId"]:
                    extracted["customer_ids"].add(booking["clientId"])
                if "bookingPets" in booking:
                    pets = booking.get("bookingPets", [])
                    if isinstance(pets, list):
                        for pet in pets:
                            if isinstance(pet, dict) and "petId" in pet and pet["petId"]:
                                extracted["pet_ids"].add(pet["petId"])
    
    # Convert sets to lists for JSON serialization
    extracted["customer_ids"] = list(extracted["customer_ids"])
    extracted["pet_ids"] = list(extracted["pet_ids"])
    
    return extracted


def extract_service_fields(service_response: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract relevant fields from services response.
    
    Args:
        service_response: List of service objects from API
        
    Returns:
        Dictionary with extracted fields:
        - service_id: First service ID if found
        - services: Full list of services
        - service_map: Map of service names to service IDs
    """
    extracted = {
        "service_id": None,
        "services": service_response if isinstance(service_response, list) else [],
        "service_map": {}
    }
    
    if isinstance(service_response, list) and len(service_response) > 0:
        # Get first service ID
        first_service = service_response[0]
        if isinstance(first_service, dict) and "id" in first_service:
            extracted["service_id"] = first_service["id"]
        
        # Create map of service names to service IDs
        for service in service_response:
            if isinstance(service, dict) and "id" in service and "name" in service:
                service_name = service["name"]
                service_id = service["id"]
                extracted["service_map"][service_name] = service_id
    
    return extracted

async def get_customer_profile(tool_context: ToolContext, pet_professional_id: str) -> str:
    """Get existing customers profiles by pet professionals id

    Args:
        tool_context: ToolContext providing access to session state
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
        # Make API call
        result = await api_client.get_customer_profiles_by_pet_professionals_id(pet_professional_id)
        
        # Extract relevant fields
        extracted = extract_customer_fields(result)
        
        # Store in session state if ToolContext is available
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" not in state:
                state["tool_results"] = {}
            state["tool_results"]["get_customer_profile"] = {
                "full_response": result,
                "extracted": extracted,
                "timestamp": time.time()
            }
        
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def create_customer(tool_context: ToolContext, customer_data_json: str) -> str:
    """Create new customer profile

    Args:
        tool_context: ToolContext providing access to session state
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
        
        # Check state for existing customer before creating
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" in state and "get_customer_profile" in state["tool_results"]:
                stored_customers = state["tool_results"]["get_customer_profile"].get("extracted", {}).get("customers", [])
                # Check if customer with same email or phone already exists
                email = customer_data.get("email")
                phone = customer_data.get("phone")
                if email or phone:
                    for existing_customer in stored_customers:
                        if isinstance(existing_customer, dict):
                            if (email and existing_customer.get("email") == email) or \
                               (phone and existing_customer.get("phone") == phone):
                                # Customer already exists, return existing customer
                                return json.dumps({
                                    "success": True,
                                    "data": existing_customer,
                                    "from_cache": True
                                })
        
        # Create new customer
        result = await api_client.create_customer(customer_data)
        
        # Update state with new customer
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" in state and "get_customer_profile" in state["tool_results"]:
                # Add new customer to cached list
                customers_list = state["tool_results"]["get_customer_profile"]["extracted"].get("customers", [])
                if isinstance(customers_list, list):
                    customers_list.append(result)
                    # Re-extract fields to update customer_id
                    state["tool_results"]["get_customer_profile"]["extracted"] = extract_customer_fields(customers_list)
        
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def create_pet_profiles(tool_context: ToolContext, customer_data_json: str) -> str:
    """Add new pet profiles to existing customer

    Args:
        tool_context: ToolContext providing access to session state
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
        customer_id = customer_data.get("id")
        
        # Try to get customer_id from state if not provided
        if not customer_id and tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" in state and "get_customer_profile" in state["tool_results"]:
                extracted = state["tool_results"]["get_customer_profile"].get("extracted", {})
                customer_id = extracted.get("customer_id")
                if customer_id:
                    customer_data["id"] = customer_id
        
        result = await api_client.create_pet_profiles(customer_data)
        
        # Update state with new pets
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" in state and "get_customer_profile" in state["tool_results"]:
                # Update customer data in cache with new pets
                customers_list = state["tool_results"]["get_customer_profile"]["extracted"].get("customers", [])
                # Find and update the customer in the list
                for i, customer in enumerate(customers_list):
                    if isinstance(customer, dict) and customer.get("id") == customer_id:
                        customers_list[i] = result
                        break
                # Re-extract fields
                state["tool_results"]["get_customer_profile"]["extracted"] = extract_customer_fields(customers_list)
        
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def get_services(tool_context: ToolContext, professional_id: str) -> str:
    """Get services information by professional id

    Args:
        tool_context: ToolContext providing access to session state
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
        # Make API call
        result = await api_client.get_services_by_professional_id(professional_id)
        
        # Extract relevant fields
        extracted = extract_service_fields(result)
        
        # Store in session state if ToolContext is available
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" not in state:
                state["tool_results"] = {}
            state["tool_results"]["get_services"] = {
                "full_response": result,
                "extracted": extracted,
                "timestamp": time.time()
            }
        
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def get_bookings(tool_context: ToolContext, professional_id: str) -> str:
    """Get all bookings for a professional

    Args:
        tool_context: ToolContext providing access to session state
        professional_id: ID of the pet professional

    Returns:
        JSON string with success status and list of booking objects, each containing:
            - id: Booking UUID
            - clientId: Customer UUID
            - serviceId: Service UUID
            - professionalId: Professional's UUID
            - serviceRateId: Service rate UUID (may be null)
            - startDate: Booking start date (YYYY-MM-DD)
            - endDate: Booking end date (YYYY-MM-DD)
            - startTime: Start time (HH:MM:SS)
            - endTime: End time (HH:MM:SS)
            - totalAmount: Total booking amount
            - notes: Booking notes
            - status: Booking status (scheduled, completed, cancelled)
            - createdAt: Creation timestamp
            - updatedAt: Last update timestamp
            - extraPetFee: Additional fee for extra pets
            - holidayFee: Holiday surcharge
            - afterHourFee: After hours surcharge
            - weekendFee: Weekend surcharge
            - extraChargesTotal: Sum of all extra charges
            - bookingPets: List of pet objects with petId and specialInstructions
            - parentBookingId: Parent booking UUID for repeating bookings (may be null)
            - isRepeating: Boolean indicating if booking repeats
            - repeatType: Type of repetition (daily, weekly, etc., may be null)
            - weeklyDays: Days of week for weekly repeats (may be null)
            - repeatUntilDate: End date for repetition (may be null)
            - maxOccurrences: Maximum number of occurrences (may be null)
            - occurrenceNumber: Current occurrence number
            - allDay: Boolean indicating if booking is all-day
    """
    try:
        # Make API call
        result = await api_client.get_bookings_by_professional_id(professional_id)
        
        # Extract relevant fields
        extracted = extract_booking_fields(result)
        
        # Store in session state if ToolContext is available
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" not in state:
                state["tool_results"] = {}
            state["tool_results"]["get_bookings"] = {
                "full_response": result,
                "extracted": extracted,
                "timestamp": time.time()
            }
        
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def create_booking(tool_context: ToolContext, booking_data_json: str) -> str:
    """Create new booking

    Args:
        tool_context: ToolContext providing access to session state
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
        
        # Try to get missing data from state
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" in state:
                tool_results = state["tool_results"]
                
                # Get customer data from state
                if "get_customer_profile" in tool_results:
                    customer_extracted = tool_results["get_customer_profile"].get("extracted", {})
                    if not booking_data.get("clientId") and customer_extracted.get("customer_id"):
                        booking_data["clientId"] = customer_extracted["customer_id"]
                
                # Get service data from state
                if "get_services" in tool_results:
                    services_extracted = tool_results["get_services"].get("extracted", {})
                    if not booking_data.get("serviceId"):
                        # Try to match service by name or use first service
                        service_map = services_extracted.get("service_map", {})
                        if service_map:
                            # Could match by name if provided, otherwise use first
                            first_service_id = services_extracted.get("service_id")
                            if first_service_id:
                                booking_data["serviceId"] = first_service_id
        
        # Make API call
        result = await api_client.create_booking(booking_data)
        
        # Update state with new booking (add to bookings cache)
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" not in state:
                state["tool_results"] = {}
            if "get_bookings" not in state["tool_results"]:
                state["tool_results"]["get_bookings"] = {"full_response": [], "extracted": {}}
            
            # Append new booking to cached bookings list
            bookings_list = state["tool_results"]["get_bookings"]["full_response"]
            if isinstance(bookings_list, list):
                bookings_list.append(result)
                # Re-extract fields
                state["tool_results"]["get_bookings"]["extracted"] = extract_booking_fields(bookings_list)
        
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


async def update_booking(tool_context: ToolContext, booking_id: str, booking_data_json: str) -> str:
    """Update existing booking

    Args:
        tool_context: ToolContext providing access to session state
        booking_id: UUID of the booking to update
        booking_data_json: JSON string of complete booking object (same schema as GET response):
            - id: Booking UUID
            - clientId: Customer UUID
            - serviceId: Service UUID
            - professionalId: Professional's UUID
            - serviceRateId: Service rate UUID (may be null)
            - startDate: Booking start date (YYYY-MM-DD)
            - endDate: Booking end date (YYYY-MM-DD)
            - startTime: Start time (HH:MM:SS or HH:MM)
            - endTime: End time (HH:MM:SS or HH:MM)
            - totalAmount: Total booking amount
            - notes: Booking notes
            - status: Booking status
            - extraPetFee: Additional fee for extra pets
            - holidayFee: Holiday surcharge
            - afterHourFee: After hours surcharge
            - weekendFee: Weekend surcharge
            - extraChargesTotal: Sum of extra charges
            - bookingPets: List of pet objects with petId and specialInstructions
            - All other fields from the existing booking

    Returns:
        JSON string with updated booking information and success status
    """
    try:
        booking_data = json.loads(booking_data_json)
        
        # Try to get missing data from state
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" in state:
                tool_results = state["tool_results"]
                
                # Get existing booking from state if available
                if "get_bookings" in tool_results:
                    bookings_list = tool_results["get_bookings"].get("full_response", [])
                    if isinstance(bookings_list, list):
                        for booking in bookings_list:
                            if isinstance(booking, dict) and booking.get("id") == booking_id:
                                # Merge existing booking data with updates
                                for key, value in booking.items():
                                    if key not in booking_data or booking_data[key] is None:
                                        booking_data[key] = value
                                break
                
                # Get customer data from state if clientId missing
                if not booking_data.get("clientId") and "get_customer_profile" in tool_results:
                    customer_extracted = tool_results["get_customer_profile"].get("extracted", {})
                    if customer_extracted.get("customer_id"):
                        booking_data["clientId"] = customer_extracted["customer_id"]
                
                # Get service data from state if serviceId missing
                if not booking_data.get("serviceId") and "get_services" in tool_results:
                    services_extracted = tool_results["get_services"].get("extracted", {})
                    if services_extracted.get("service_id"):
                        booking_data["serviceId"] = services_extracted["service_id"]
        
        result = await api_client.update_booking(booking_id, booking_data)
        
        # Update state with updated booking
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" in state and "get_bookings" in state["tool_results"]:
                bookings_list = state["tool_results"]["get_bookings"]["full_response"]
                if isinstance(bookings_list, list):
                    # Update existing booking in cache
                    for i, booking in enumerate(bookings_list):
                        if isinstance(booking, dict) and booking.get("id") == booking_id:
                            bookings_list[i] = result
                            break
                    # Re-extract fields
                    state["tool_results"]["get_bookings"]["extracted"] = extract_booking_fields(bookings_list)
        
        return json.dumps({
            "success": True,
            "data": result
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })


# Helper functions for matching and formatting
def match_customer(customers: List[Dict[str, Any]], email: Optional[str] = None, phone: Optional[str] = None, name: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Match customer by email, phone, or name."""
    if not customers:
        return None
    
    for customer in customers:
        if not isinstance(customer, dict):
            continue
        
        # Match by email
        if email and customer.get("email") and customer.get("email").lower() == email.lower():
            return customer
        
        # Match by phone
        if phone and customer.get("phone") and customer.get("phone") == phone:
            return customer
        
        # Match by name
        if name:
            customer_name = f"{customer.get('firstName', '')} {customer.get('lastName', '')}".strip().lower()
            if customer_name and name.lower() in customer_name or customer_name in name.lower():
                return customer
    
    return None


def match_pet(pets: List[Dict[str, Any]], pet_name: str) -> Optional[Dict[str, Any]]:
    """Match pet by name with fuzzy matching for typos (case-insensitive)."""
    if not pets or not pet_name:
        return None
    
    pet_name_lower = pet_name.lower().strip()
    
    # First try exact match
    for pet in pets:
        if isinstance(pet, dict):
            existing_name = pet.get("name", "").lower().strip()
            if existing_name == pet_name_lower:
                return pet
    
    # If fuzzy matching available, try fuzzy match (handles typos)
    if HAS_FUZZY_MATCHING:
        best_match = None
        best_score = 0
        threshold = 85  # 85% similarity threshold for typos
        
        for pet in pets:
            if isinstance(pet, dict):
                existing_name = pet.get("name", "").lower().strip()
                if existing_name:
                    # Use ratio for overall similarity
                    score = fuzz.ratio(pet_name_lower, existing_name)
                    if score > best_score and score >= threshold:
                        best_score = score
                        best_match = pet
        
        if best_match:
            return best_match
    
    # Fallback: partial match (substring)
    for pet in pets:
        if isinstance(pet, dict):
            existing_name = pet.get("name", "").lower().strip()
            if pet_name_lower in existing_name or existing_name in pet_name_lower:
                return pet
    
    return None


def match_service_semantic(services: List[Dict[str, Any]], service_request: str) -> Optional[Dict[str, Any]]:
    """Semantically match service request to available services with improved logic to prevent false matches."""
    if not services or not service_request:
        return None
    
    service_request_lower = service_request.lower().strip()
    
    # Keywords for semantic matching - prioritized and more specific to avoid overlap
    # Higher priority keywords come first in each list
    keywords = {
        "pet sitting": [
            "pet sitting", "pet sitter", "sitting", "overnight", "overnight care",
            "watch", "watch my", "look after", "look after my",
            "care for", "care for my", "pet care", "dog sitting", "cat sitting",
            "babysit", "babysitting", "pet babysitting", "stay with", "stay with my",
            "house sit", "house sitting", "pet house sitting"
        ],
        "dog walking": [
            "dog walking", "dog walker", "walk", "walk my dog",
            "take my dog for a walk", "dog walk", "take dog out", "walk the dog",
            "daily walk", "regular walk"
        ],
        "grooming": [
            "grooming", "groom", "bath", "bathe", "bathe my", "wash",
            "wash my", "pet grooming", "dog grooming", "cat grooming", "nail trim",
            "nail clipping", "haircut", "hair cut", "trim"
        ]
    }
    
    # Score services based on match quality (higher score = better match)
    scored_services = []
    
    for service in services:
        if not isinstance(service, dict):
            continue
        
        service_name = service.get("name", "").lower().strip()
        score = 0
        
        # Priority 1: Exact match (highest priority)
        if service_request_lower == service_name:
            score = 1000
        elif service_request_lower in service_name or service_name in service_request_lower:
            score = 900
        
        # Priority 2: Semantic keyword match (check each service type)
        for service_type, keyword_list in keywords.items():
            # Check if request contains keywords for this service type
            request_has_keywords = any(kw in service_request_lower for kw in keyword_list)
            # Check if service name contains the service type
            service_has_type = service_type in service_name
            
            if request_has_keywords and service_has_type:
                # Find the highest priority keyword that matches
                for idx, kw in enumerate(keyword_list):
                    if kw in service_request_lower:
                        # Higher priority keywords (earlier in list) get higher scores
                        priority_score = (len(keyword_list) - idx) * 10
                        score = max(score, 500 + priority_score)
                        break
        
        # Priority 3: Word overlap (lower priority, only if no better match)
        if score < 500:
            service_words = set(service_name.split())
            request_words = set(service_request_lower.split())
            common_words = service_words.intersection(request_words)
            # Remove common stop words that don't help matching
            stop_words = {"pet", "my", "the", "a", "an", "for", "of", "with"}
            meaningful_common = common_words - stop_words
            if meaningful_common:
                score = max(score, len(meaningful_common) * 10)
        
        if score > 0:
            scored_services.append((score, service))
    
    # Return the highest scoring service
    if scored_services:
        scored_services.sort(key=lambda x: x[0], reverse=True)
        return scored_services[0][1]
    
    return None


def format_customer_result(customer: Dict[str, Any], status: str, source: str = "api") -> str:
    """Format customer data into agent output JSON."""
    return json.dumps({
        "customer_id": customer.get("id"),
        "professional_id": customer.get("professionalId"),
        "status": status,
        "customer_name": f"{customer.get('firstName', '')} {customer.get('lastName', '')}".strip(),
        "existing_pets": customer.get("pets", []),
        "source": source,
        "message": f"Customer {status}"
    })


def format_pet_result(customer_id: str, professional_id: str, pet_ids: List[str], pet_names: List[str], pet_species: List[str], status: str, source: str = "api", message: str = "") -> str:
    """Format pet data into agent output JSON."""
    return json.dumps({
        "customer_id": customer_id,
        "professional_id": professional_id,
        "pet_ids": pet_ids,
        "pet_names": pet_names,
        "pet_species": pet_species,
        "status": status,
        "source": source,
        "message": message
    })


def format_service_result(service_id: str, professional_id: str, service_name: str, service_rate_id: Optional[str], service_rate: Optional[float], status: str, source: str = "api", message: str = "") -> str:
    """Format service data into agent output JSON."""
    return json.dumps({
        "service_id": service_id,
        "professional_id": professional_id,
        "service_name": service_name,
        "service_rate_id": service_rate_id,
        "service_rate": service_rate,
        "status": status,
        "source": source,
        "message": message
    })


# State-aware wrapper tools
async def ensure_customer_exists(
    tool_context: ToolContext,
    professional_id: str,
    customer_name: Optional[str] = None,
    customer_email: Optional[str] = None,
    customer_phone: Optional[str] = None
) -> str:
    """Ensure customer exists. Checks state first, then API if needed.
    
    Args:
        tool_context: ToolContext providing access to session state
        professional_id: ID of the pet professional
        customer_name: Customer's full name
        customer_email: Customer's email address
        customer_phone: Customer's phone number
    
    Returns:
        JSON string with formatted customer result ready for agent output
    """
    state = tool_context.state if tool_context and hasattr(tool_context, 'state') else {}
    
    # Check state for existing customer
    if "tool_results" in state and "get_customer_profile" in state["tool_results"]:
        customers = state["tool_results"]["get_customer_profile"].get("extracted", {}).get("customers", [])
        matched = match_customer(customers, customer_email, customer_phone, customer_name)
        if matched:
            return format_customer_result(matched, "found", "state")
    
    # Not in state - check API
    result_json = await get_customer_profile(tool_context, professional_id)
    result = json.loads(result_json)
    
    if result.get("success") and result.get("data"):
        customers = result["data"]
        matched = match_customer(customers, customer_email, customer_phone, customer_name)
        if matched:
            return format_customer_result(matched, "found", "api")
    
    # Not found - create
    if not customer_name and not customer_email and not customer_phone:
        return json.dumps({
            "customer_id": None,
            "professional_id": professional_id,
            "status": "insufficient_data",
            "customer_name": "",
            "existing_pets": [],
            "source": "api",
            "message": "Insufficient data to create customer"
        })
    
    # Parse name into first/last
    name_parts = customer_name.split() if customer_name else []
    customer_data = {
        "firstName": name_parts[0] if name_parts else "",
        "lastName": " ".join(name_parts[1:]) if len(name_parts) > 1 else "",
        "email": customer_email or "",
        "phone": customer_phone or "",
        "professionalId": professional_id
    }
    
    create_result = await create_customer(tool_context, json.dumps(customer_data))
    create_data = json.loads(create_result)
    
    if create_data.get("success") and create_data.get("data"):
        return format_customer_result(create_data["data"], "created", "api")
    
    return json.dumps({
        "customer_id": None,
        "professional_id": professional_id,
        "status": "error",
        "customer_name": customer_name or "",
        "existing_pets": [],
        "source": "api",
        "message": f"Error creating customer: {create_data.get('error', 'Unknown error')}"
    })


async def ensure_pets_exist(
    tool_context: ToolContext,
    pets_info: str
) -> str:
    """Ensure pets exist. Gets customer_id from state, checks for existing pets, creates/updates as needed.
    
    Args:
        tool_context: ToolContext providing access to session state
        pets_info: JSON string with list of pet objects, each with name, species, breed, and optionally age
    
    Returns:
        JSON string with formatted pet result ready for agent output
    """
    try:
        pets_data = json.loads(pets_info) if isinstance(pets_info, str) else pets_info
        if not isinstance(pets_data, list):
            pets_data = [pets_data]
        
        state = tool_context.state if tool_context and hasattr(tool_context, 'state') else {}
        
        # Get customer_id from state
        customer_id = None
        professional_id = None
        existing_pets = []
        
        if "tool_results" in state and "get_customer_profile" in state["tool_results"]:
            customer_extracted = state["tool_results"]["get_customer_profile"].get("extracted", {})
            customer_id = customer_extracted.get("customer_id")
            customers = customer_extracted.get("customers", [])
            if customers and isinstance(customers, list) and len(customers) > 0:
                first_customer = customers[0]
                if isinstance(first_customer, dict):
                    professional_id = first_customer.get("professionalId")
                    existing_pets = first_customer.get("pets", [])
        
        if not customer_id:
            return json.dumps({
                "customer_id": None,
                "professional_id": professional_id,
                "pet_ids": [],
                "pet_names": [],
                "pet_species": [],
                "status": "insufficient_data",
                "source": "api",
                "message": "Customer ID not found in state. Ensure customer_agent runs first."
            })
        
        # Match existing pets and determine what to create/update
        pets_to_create = []
        pets_to_update = []
        matched_pet_ids = []
        matched_pet_names = []
        matched_pet_species = []
        
        for pet_info in pets_data:
            if not isinstance(pet_info, dict):
                continue
            
            pet_name = pet_info.get("name")
            if not pet_name:
                continue
            
            # Check if pet already exists
            existing_pet = match_pet(existing_pets, pet_name)
            
            if existing_pet:
                # Pet exists - check if update needed
                pet_id = existing_pet.get("id")
                matched_pet_ids.append(pet_id)
                matched_pet_names.append(pet_name)
                matched_pet_species.append(pet_info.get("species", existing_pet.get("species", "")))
                
                # Check if update needed (new breed, age, etc.)
                needs_update = False
                if pet_info.get("breed") and pet_info.get("breed") != existing_pet.get("breed"):
                    needs_update = True
                
                if needs_update:
                    pet_info["id"] = pet_id
                    pet_info["ownerId"] = customer_id
                    pets_to_update.append(pet_info)
            else:
                # Pet doesn't exist - create
                pet_info["ownerId"] = customer_id
                # Set defaults for optional fields
                if "gender" not in pet_info:
                    pet_info["gender"] = "Male"
                pets_to_create.append(pet_info)
        
        # If all pets exist and no updates needed, return immediately
        if not pets_to_create and not pets_to_update and matched_pet_ids:
            return format_pet_result(
                customer_id, professional_id, matched_pet_ids, matched_pet_names, matched_pet_species,
                "found", "state", "All pets found in state"
            )
        
        # Create/update pets if needed
        if pets_to_create or pets_to_update:
            all_pets = pets_to_update + pets_to_create
            customer_data = {
                "id": customer_id,
                "professionalId": professional_id,
                "pets": all_pets
            }
            
            result_json = await create_pet_profiles(tool_context, json.dumps(customer_data))
            result = json.loads(result_json)
            
            if result.get("success") and result.get("data"):
                # Extract pet IDs from result
                updated_pets = result["data"].get("pets", [])
                final_pet_ids = []
                final_pet_names = []
                final_pet_species = []
                
                for pet_info in pets_data:
                    pet_name = pet_info.get("name")
                    if pet_name:
                        # Find in updated pets
                        for updated_pet in updated_pets:
                            if isinstance(updated_pet, dict) and updated_pet.get("name") == pet_name:
                                final_pet_ids.append(updated_pet.get("id"))
                                final_pet_names.append(pet_name)
                                final_pet_species.append(updated_pet.get("species", pet_info.get("species", "")))
                                break
                
                # Combine with matched pets
                final_pet_ids = matched_pet_ids + final_pet_ids
                final_pet_names = matched_pet_names + final_pet_names
                final_pet_species = matched_pet_species + final_pet_species
                
                status = "created" if pets_to_create else "updated"
                if pets_to_create and pets_to_update:
                    status = "updated"
                
                return format_pet_result(
                    customer_id, professional_id, final_pet_ids, final_pet_names, final_pet_species,
                    status, "api", f"Pets {status} successfully"
                )
        
        # Return matched pets if no API call was needed
        return format_pet_result(
            customer_id, professional_id, matched_pet_ids, matched_pet_names, matched_pet_species,
            "found", "state", "All pets found in state"
        )
        
    except Exception as e:
        return json.dumps({
            "customer_id": None,
            "professional_id": None,
            "pet_ids": [],
            "pet_names": [],
            "pet_species": [],
            "status": "error",
            "source": "api",
            "message": f"Error ensuring pets exist: {str(e)}"
        })


async def match_service(
    tool_context: ToolContext,
    professional_id: str,
    service_request: str
) -> str:
    """Match service request to available services using semantic matching.
    
    Args:
        tool_context: ToolContext providing access to session state
        professional_id: ID of the pet professional
        service_request: Service type requested (e.g., "pet sitting", "dog walking")
    
    Returns:
        JSON string with matched service information
    """
    state = tool_context.state if tool_context and hasattr(tool_context, 'state') else {}
    
    # Check state first
    services = None
    if "tool_results" in state and "get_services" in state["tool_results"]:
        services = state["tool_results"]["get_services"].get("full_response", [])
    
    # If not in state, fetch from API
    if not services:
        result_json = await get_services(tool_context, professional_id)
        result = json.loads(result_json)
        if result.get("success"):
            services = result.get("data", [])
    
    if not services:
        return json.dumps({
            "matched_service_id": None,
            "service_name": None,
            "service_rate_id": None,
            "service_rate": None,
            "available_services": [],
            "message": "No services available"
        })
    
    # Perform semantic matching
    matched = match_service_semantic(services, service_request)
    
    if matched:
        # Extract service rate and service rate ID
        service_rate = matched.get("amount")
        service_rate_id = None
        
        if "serviceRate" in matched and isinstance(matched["serviceRate"], dict):
            service_rate_obj = matched["serviceRate"]
            # Extract service rate ID (required for booking creation)
            service_rate_id = service_rate_obj.get("id")
            # Extract amount if not already found
            if service_rate is None:
                service_rate = service_rate_obj.get("amount")
        
        return json.dumps({
            "matched_service_id": matched.get("id"),
            "service_name": matched.get("name"),
            "service_rate_id": service_rate_id,
            "service_rate": service_rate,
            "available_services": [s.get("name") for s in services if isinstance(s, dict) and s.get("name")],
            "message": f"Matched service: {matched.get('name')}"
        })
    
    # No match found
    return json.dumps({
        "matched_service_id": None,
        "service_name": None,
        "service_rate_id": None,
        "service_rate": None,
        "available_services": [s.get("name") for s in services if isinstance(s, dict) and s.get("name")],
        "message": f"No matching service found for: {service_request}"
    })


async def ensure_service_matched(
    tool_context: ToolContext,
    professional_id: str,
    service_request: str
) -> str:
    """Ensure service is matched. Checks state first, then matches service semantically and validates rate.
    
    Args:
        tool_context: ToolContext providing access to session state
        professional_id: ID of the pet professional
        service_request: Service type requested (e.g., "pet sitting", "dog walking")
    
    Returns:
        JSON string with formatted service result ready for agent output
    """
    try:
        state = tool_context.state if tool_context and hasattr(tool_context, 'state') else {}
        
        # Check state first for existing service match
        service_id = None
        service_name = None
        service_rate_id = None
        service_rate = None
        source = "state"
        
        if "tool_results" in state and "service_result" in state["tool_results"]:
            service_extracted = state["tool_results"]["service_result"].get("extracted", {})
            if service_extracted.get("service_id") and service_extracted.get("service_request") == service_request:
                service_id = service_extracted.get("service_id")
                service_name = service_extracted.get("service_name")
                service_rate_id = service_extracted.get("service_rate_id")
                service_rate = service_extracted.get("service_rate")
                return format_service_result(
                    service_id=service_id,
                    professional_id=professional_id,
                    service_name=service_name,
                    service_rate_id=service_rate_id,
                    service_rate=service_rate,
                    status="found",
                    source=source,
                    message=f"Service matched from state: {service_name}"
                )
        
        # If not in state, match service
        source = "api"
        match_result_json = await match_service(tool_context, professional_id, service_request)
        match_result = json.loads(match_result_json)
        
        service_id = match_result.get("matched_service_id")
        service_name = match_result.get("service_name")
        service_rate_id = match_result.get("service_rate_id")
        service_rate = match_result.get("service_rate")
        
        if not service_id:
            return format_service_result(
                service_id=None,
                professional_id=professional_id,
                service_name=None,
                service_rate_id=None,
                service_rate=None,
                status="not_found",
                source=source,
                message=f"No matching service found for: {service_request}. Available services: {', '.join(match_result.get('available_services', []))}"
            )
        
        # Validate that service rate exists
        if not service_rate_id:
            return format_service_result(
                service_id=service_id,
                professional_id=professional_id,
                service_name=service_name,
                service_rate_id=None,
                service_rate=service_rate,
                status="rate_missing",
                source=source,
                message=f"Service '{service_name}' matched but service rate is not configured. Please configure service rate before creating booking."
            )
        
        # Store in state
        if tool_context and hasattr(tool_context, 'state'):
            state = tool_context.state
            if "tool_results" not in state:
                state["tool_results"] = {}
            state["tool_results"]["service_result"] = {
                "extracted": {
                    "service_id": service_id,
                    "service_name": service_name,
                    "service_rate_id": service_rate_id,
                    "service_rate": service_rate,
                    "service_request": service_request
                },
                "timestamp": time.time()
            }
        
        return format_service_result(
            service_id=service_id,
            professional_id=professional_id,
            service_name=service_name,
            service_rate_id=service_rate_id,
            service_rate=service_rate,
            status="matched",
            source=source,
            message=f"Service matched successfully: {service_name}"
        )
        
    except Exception as e:
        return format_service_result(
            service_id=None,
            professional_id=professional_id,
            service_name=None,
            service_rate_id=None,
            service_rate=None,
            status="error",
            source="api",
            message=f"Error matching service: {str(e)}"
        )


async def ensure_booking_exists(
    tool_context: ToolContext,
    professional_id: str,
    date_phrase: str,
    notes: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None
) -> str:
    """Ensure booking exists. Gets customer_id, pet_ids, and service info from state, calculates dates, creates/updates booking.
    
    Args:
        tool_context: ToolContext providing access to session state
        professional_id: ID of the pet professional
        date_phrase: Date phrase from conversation (e.g., "next weekend", "Saturday 8 AM to Sunday 6 PM")
        notes: Optional booking notes
        start_date: Optional calculated start date (YYYY-MM-DD) from date_calculation_agent
        end_date: Optional calculated end date (YYYY-MM-DD) from date_calculation_agent
        start_time: Optional calculated start time (HH:MM) from date_calculation_agent
        end_time: Optional calculated end time (HH:MM) from date_calculation_agent
    
    Returns:
        JSON string with formatted booking result ready for agent output
    """
    try:
        state = tool_context.state if tool_context and hasattr(tool_context, 'state') else {}
        
        # Get customer_id and pet_ids from state
        customer_id = None
        pet_ids = []
        professional_id_from_state = professional_id
        
        if "tool_results" in state:
            tool_results = state["tool_results"]
            
            # Get customer_id
            if "get_customer_profile" in tool_results:
                customer_extracted = tool_results["get_customer_profile"].get("extracted", {})
                customer_id = customer_extracted.get("customer_id")
                customers = customer_extracted.get("customers", [])
                if customers and isinstance(customers, list) and len(customers) > 0:
                    first_customer = customers[0]
                    if isinstance(first_customer, dict):
                        professional_id_from_state = first_customer.get("professionalId", professional_id)
                        # Get pets from customer
                        pets = first_customer.get("pets", [])
                        pet_ids = [p.get("id") for p in pets if isinstance(p, dict) and p.get("id")]
        
        if not customer_id or not pet_ids:
            return json.dumps({
                "customer_id": customer_id,
                "professional_id": professional_id_from_state,
                "pet_ids": pet_ids,
                "matched_service_id": None,
                "service_name": None,
                "service_rate_id": None,
                "service_rate": None,
                "start_date": None,
                "end_date": None,
                "start_time": None,
                "end_time": None,
                "booking_id_from_history": None,
                "existing_booking_found": "not_found",
                "existing_booking_id": None,
                "action_taken": "error",
                "booking_id": None,
                "status": "insufficient_data",
                "source": "api",
                "message": "Customer ID or pet IDs not found in state. Ensure customer_agent and pet_agent run first."
            })
        
        # Get service_id and service_rate_id from state (from service_agent)
        matched_service_id = None
        service_name = None
        service_rate_id = None
        service_rate = None
        
        if "tool_results" in state and "service_result" in state["tool_results"]:
            service_extracted = state["tool_results"]["service_result"].get("extracted", {})
            matched_service_id = service_extracted.get("service_id")
            service_name = service_extracted.get("service_name")
            service_rate_id = service_extracted.get("service_rate_id")
            service_rate = service_extracted.get("service_rate")
        
        if not matched_service_id:
            return json.dumps({
                "customer_id": customer_id,
                "professional_id": professional_id_from_state,
                "pet_ids": pet_ids,
                "matched_service_id": None,
                "service_name": None,
                "service_rate_id": None,
                "service_rate": None,
                "start_date": None,
                "end_date": None,
                "start_time": None,
                "end_time": None,
                "booking_id_from_history": None,
                "existing_booking_found": "not_found",
                "existing_booking_id": None,
                "action_taken": "error",
                "booking_id": None,
                "status": "insufficient_data",
                "source": "api",
                "message": "Service ID not found in state. Ensure service_agent runs before booking_creation_agent."
            })
        
        if not service_rate_id:
            return json.dumps({
                "customer_id": customer_id,
                "professional_id": professional_id_from_state,
                "pet_ids": pet_ids,
                "matched_service_id": matched_service_id,
                "service_name": service_name,
                "service_rate_id": None,
                "service_rate": service_rate,
                "start_date": None,
                "end_date": None,
                "start_time": None,
                "end_time": None,
                "booking_id_from_history": None,
                "existing_booking_found": "not_found",
                "existing_booking_id": None,
                "action_taken": "error",
                "booking_id": None,
                "status": "rate_missing",
                "source": "api",
                "message": f"Service '{service_name}' matched but service rate ID is missing. Service rate must be configured before creating booking."
            })
        
        # Get calculated dates from state (from date_calculation_agent in booking_sequential_agent)
        calculated_start_date = start_date
        calculated_end_date = end_date
        calculated_start_time = start_time
        calculated_end_time = end_time
        
        # Check state for date_calculation_agent results
        if "tool_results" in state:
            tool_results = state["tool_results"]
            # Look for date calculation results from date_calculation_agent output
            # The date_calculation_agent outputs via output_key="date_result"
            # Check conversation history or state for date_result
            if "date_result" in tool_results:
                date_result = tool_results["date_result"]
                if isinstance(date_result, dict):
                    calculated_start_date = date_result.get("start_date") or calculated_start_date
                    calculated_end_date = date_result.get("end_date") or calculated_end_date
                    calculated_start_time = date_result.get("start_time") or calculated_start_time
                    calculated_end_time = date_result.get("end_time") or calculated_end_time
                elif isinstance(date_result, str):
                    # Try to parse JSON string
                    try:
                        date_data = json.loads(date_result)
                        calculated_start_date = date_data.get("start_date") or calculated_start_date
                        calculated_end_date = date_data.get("end_date") or calculated_end_date
                        calculated_start_time = date_data.get("start_time") or calculated_start_time
                        calculated_end_time = date_data.get("end_time") or calculated_end_time
                    except:
                        pass
        
        # If dates not provided and not in state, try to parse date_phrase directly as fallback
        if not calculated_start_date and date_phrase:
            # Try basic parsing for common patterns
            try:
                from datetime import datetime, timedelta
                import re
                
                # Get current date from config
                from ..config import CURRENT_DATE
                current = datetime.strptime(CURRENT_DATE, "%Y-%m-%d")
                
                # Simple parsing for "next weekend", "next Saturday", etc.
                date_phrase_lower = date_phrase.lower()
                
                # Parse "next weekend" or "next Saturday to Sunday"
                if "next weekend" in date_phrase_lower or ("next saturday" in date_phrase_lower and "sunday" in date_phrase_lower):
                    # Find next Saturday
                    days_until_saturday = (5 - current.weekday()) % 7
                    if days_until_saturday == 0:
                        days_until_saturday = 7  # If today is Saturday, get next Saturday
                    next_saturday = current + timedelta(days=days_until_saturday)
                    next_sunday = next_saturday + timedelta(days=1)
                    calculated_start_date = next_saturday.strftime("%Y-%m-%d")
                    calculated_end_date = next_sunday.strftime("%Y-%m-%d")
                    
                    # Parse times if mentioned - look for "8 AM" and "6 PM" patterns
                    time_matches = re.findall(r'(\d+)\s*(AM|PM)', date_phrase, re.IGNORECASE)
                    if len(time_matches) >= 1:
                        hour = int(time_matches[0][0])
                        am_pm = time_matches[0][1].upper()
                        if am_pm == "PM" and hour != 12:
                            hour += 12
                        elif am_pm == "AM" and hour == 12:
                            hour = 0
                        calculated_start_time = f"{hour:02d}:00"
                    
                    if len(time_matches) >= 2:
                        hour = int(time_matches[1][0])
                        am_pm = time_matches[1][1].upper()
                        if am_pm == "PM" and hour != 12:
                            hour += 12
                        elif am_pm == "AM" and hour == 12:
                            hour = 0
                        calculated_end_time = f"{hour:02d}:00"
            except Exception as e:
                # If parsing fails, dates will remain None and we'll use placeholders
                pass
        
        # Use calculated dates or fallback to placeholders
        final_start_date = calculated_start_date
        final_end_date = calculated_end_date
        final_start_time = calculated_start_time
        final_end_time = calculated_end_time
        
        # If still no dates, use placeholders as last resort (should not happen if date_calculation_agent was called)
        if not final_start_date:
            final_start_date = "2024-01-01"
            final_end_date = "2024-01-01"
            final_start_time = "00:00"
            final_end_time = "23:59"
        
        # Check state for existing booking
        existing_booking_id = None
        existing_booking_found = "not_found"
        
        if "tool_results" in state and "get_bookings" in state["tool_results"]:
            bookings = state["tool_results"]["get_bookings"].get("full_response", [])
            if isinstance(bookings, list):
                for booking in bookings:
                    if isinstance(booking, dict):
                        # Match by customer_id, pet_ids, and dates (if we have dates)
                        if booking.get("clientId") == customer_id:
                            booking_pets = booking.get("bookingPets", [])
                            booking_pet_ids = [p.get("petId") for p in booking_pets if isinstance(p, dict)]
                            if set(pet_ids) == set(booking_pet_ids) and booking.get("status") == "scheduled":
                                existing_booking_id = booking.get("id")
                                existing_booking_found = "found_via_api"
                                break
        
        # Create or update booking
        if existing_booking_id:
            # Update existing booking
            # Get full booking object
            bookings_result_json = await get_bookings(tool_context, professional_id)
            bookings_result = json.loads(bookings_result_json)
            
            if bookings_result.get("success"):
                bookings = bookings_result.get("data", [])
                existing_booking = None
                for booking in bookings:
                    if isinstance(booking, dict) and booking.get("id") == existing_booking_id:
                        existing_booking = booking
                        break
                
                if existing_booking:
                    # Update booking with new dates if provided
                    if final_start_date and final_end_date:
                        existing_booking["startDate"] = final_start_date
                        existing_booking["endDate"] = final_end_date
                    if final_start_time:
                        existing_booking["startTime"] = final_start_time
                    if final_end_time:
                        existing_booking["endTime"] = final_end_time
                    if notes:
                        existing_booking["notes"] = notes
                    
                    update_result_json = await update_booking(tool_context, existing_booking_id, json.dumps(existing_booking))
                    update_result = json.loads(update_result_json)
                    
                    if update_result.get("success"):
                        return json.dumps({
                            "customer_id": customer_id,
                            "professional_id": professional_id_from_state,
                            "pet_ids": pet_ids,
                            "matched_service_id": matched_service_id,
                            "service_name": service_name,
                            "service_rate_id": service_rate_id,
                            "service_rate": service_rate,
                            "start_date": final_start_date or existing_booking.get("startDate"),
                            "end_date": final_end_date or existing_booking.get("endDate"),
                            "start_time": final_start_time or existing_booking.get("startTime"),
                            "end_time": final_end_time or existing_booking.get("endTime"),
                            "booking_id_from_history": existing_booking_id,
                            "existing_booking_found": "found_via_api",
                            "existing_booking_id": existing_booking_id,
                            "action_taken": "updated",
                            "booking_id": existing_booking_id,
                            "status": "updated",
                            "source": "api",
                            "message": "Booking updated successfully"
                        })
        
        # Create new booking
        booking_data = {
            "clientId": customer_id,
            "serviceId": matched_service_id,
            "serviceRateId": service_rate_id,
            "professionalId": professional_id_from_state,
            "startDate": final_start_date,
            "endDate": final_end_date,
            "startTime": final_start_time,
            "endTime": final_end_time,
            "bookingPets": [{"petId": pid} for pid in pet_ids],
            "notes": notes or "",
            "extraPetFee": 0,
            "weekendFee": 0
        }
        
        create_result_json = await create_booking(tool_context, json.dumps(booking_data))
        create_result = json.loads(create_result_json)
        
        if create_result.get("success") and create_result.get("data"):
            booking = create_result["data"]
            return json.dumps({
                "customer_id": customer_id,
                "professional_id": professional_id_from_state,
                "pet_ids": pet_ids,
                "matched_service_id": matched_service_id,
                "service_name": service_name,
                "service_rate_id": service_rate_id,
                "service_rate": service_rate,
                "start_date": booking.get("startDate"),
                "end_date": booking.get("endDate"),
                "start_time": booking.get("startTime"),
                "end_time": booking.get("endTime"),
                "booking_id_from_history": None,
                "existing_booking_found": "not_found",
                "existing_booking_id": None,
                "action_taken": "created",
                "booking_id": booking.get("id"),
                "status": "created",
                "source": "api",
                "message": "Booking created successfully"
            })
        
        return json.dumps({
            "customer_id": customer_id,
            "professional_id": professional_id_from_state,
            "pet_ids": pet_ids,
            "matched_service_id": matched_service_id,
            "service_name": service_name,
            "service_rate_id": service_rate_id,
            "service_rate": service_rate,
            "start_date": None,
            "end_date": None,
            "start_time": None,
            "end_time": None,
            "booking_id_from_history": None,
            "existing_booking_found": "not_found",
            "existing_booking_id": None,
            "action_taken": "error",
            "booking_id": None,
            "status": "error",
            "source": "api",
            "message": f"Error creating booking: {create_result.get('error', 'Unknown error')}"
        })
        
    except Exception as e:
        return json.dumps({
            "customer_id": None,
            "professional_id": professional_id,
            "pet_ids": [],
            "matched_service_id": None,
            "service_name": None,
            "service_rate_id": None,
            "service_rate": None,
            "start_date": None,
            "end_date": None,
            "start_time": None,
            "end_time": None,
            "booking_id_from_history": None,
            "existing_booking_found": "not_found",
            "existing_booking_id": None,
            "action_taken": "error",
            "booking_id": None,
            "status": "error",
            "source": "api",
            "message": f"Error ensuring booking exists: {str(e)}"
        })

