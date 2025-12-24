from typing import List, Dict, Optional
import re
from log import log
class Lead:
    """
    Represents a single business lead in the pipeline, with a built-in
    method to serialize itself for database insertion.
    """
    def __init__(self, id: int, name: str, phone: str, address: str, city: str, email: str = None,
                images=None, status: int = 0):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.city = city
        self.images = images if images is not None else []
        self.images_description={}
        self.status = status
    def __str__(self):
        return f"id:{self.id}, name:{self.name}, status:{self.status})"
    def __repr__(self):
        return f"Lead(id={self.id}, name='{self.name}', phone='{self.phone}', address='{self.address}', city='{self.city}', images='{self.images}' status={self.status})"

    def change_status(self, s:int):
        self.status=s


    def to_dict(self) -> Dict:
        """
        Converts the Lead instance into a dictionary suitable for
        database or API interaction.
        """
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'email': self.email,
            'images': self.images,
            'status': self.status
        }

    def add_images(self, images:List, descr:bool = False) -> int:
        for img in images:
            self.images.append(img)
        log(f"added images to lead: {images}")
        return 0

    def add_images_description(self, images_with_description: dict) -> dict:
        self.images_description=images_with_description
        return self.images_description

    @classmethod
    def from_map_data(cls, lead_id: int, result: dict, city: str, website_status: str):
        """Creates a Lead instance from Google Maps API result data."""

        # Google Maps API often combines address into 'formatted_address'.
        full_address = result.get('formatted_address', 'N/A')

        # Clean phone number
        phone_raw = result.get('formatted_phone_number', '') or 'N/A'
        phone = re.sub(r'[^\d\+]', '', phone_raw)

        # Extract email if available
        email = result.get('email', None)  # returns None if not present

        return cls(
            id=lead_id,
            name=result.get('name', 'N/A'),
            phone=phone,
            email=email,
            address=full_address,
            city=city,
            images=[],
            status=0
        )




