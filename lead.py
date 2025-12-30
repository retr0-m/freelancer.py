from typing import List, Dict, Optional
import re
from log import log
from config import TEMP_PATH
from languages_support import LocaleInfo
import find_lead_instagram
import screenshot_website
import json
from config import TEMP_PATH
class Lead:
    """
    Represents a single business lead in the pipeline, with a built-in
    method to serialize itself for database insertion.
    """
    def __init__(
        self,
        id: int,
        name: str,
        phone: str,
        address: str,
        city: str,
        email: str = None,
        images=None,
        status: int = 0,
        instagram: str | None = None
    ):
        self.id = id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.city = city
        self.images = images if images is not None else []
        self.images_description = {}
        self.status = status
        self.instagram = instagram
        self.localeinfo = None
    def __str__(self):
        return f"id:{self.id}, name:{self.name}, status:{self.status})"
    def __repr__(self):
        return f"Lead(id={self.id}, name='{self.name}', phone='{self.phone}', address='{self.address}', city='{self.city}', images='{self.images}' status={self.status})"

    def get_absolute_images_paths(self) -> list[str]:
        return [(TEMP_PATH+"/"+str(self.id)+"/"+path) for path in self.images]

    def change_status(self, s:int):
        self.status=s

    def fetch_localeinfo(self) -> None:
        self.localeinfo: LocaleInfo = LocaleInfo(self.address)

    def record_preview(self): # * AVAILABLE FOR SERVER VERSION

        screenshot_website.html_file_to_scrolling_video(
            html_path=TEMP_PATH+"/"+str(self.id)+"/index.html",
            output_dir=TEMP_PATH+"/"+str(self.id)+"/videos",
            width=390,
            height=844,
            scroll_step=20,
            scroll_delay=0.03
        )
        screenshot_website.html_file_to_scrolling_video(
            html_path=TEMP_PATH+"/"+str(self.id)+"/index.html",
            output_dir=TEMP_PATH+"/"+str(self.id)+"/videos",
            width=1440,
            height=900,
            scroll_step=20,
            scroll_delay=0.03
        )

    def fetch_instagram(self) -> str | None:
        """
        Attempts to discover and set the Instagram handle for this lead.
        """
        if self.instagram is not None:
            log(f"[LEAD] Instagram already set for lead {self.id}: {self.instagram}")
            return self.instagram

        log(f"[LEAD] Fetching Instagram for lead {self.id}")
        result = find_lead_instagram.from_lead(self)

        if result:
            self.instagram = result["handle"]
            log(f"[LEAD] Instagram set for lead {self.id}: {self.instagram}")
        else:
            log(f"[LEAD] No Instagram found for lead {self.id}")

        return self.instagram

    def to_dict(self) -> Dict:
        """
        Converts the Lead instance into a dictionary suitable for
        database or API interaction.
        """
        data = {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "city": self.city,
            "images": self.images,
            "status": self.status,
        }

        if hasattr(self, "localeinfo") and self.localeinfo:
            data["country_code"] = self.localeinfo.country_code
            data["currency"] = self.localeinfo.currency
            data["language_codes"] = json.dumps(self.localeinfo.language_codes)

        return data

    # ! OBSOLETE IN SERVER VERSION
    def add_images(self, images:List, descr:bool = False) -> int:
        for img in images:
            self.images.append(img)
        log(f"added images to lead: {images}")
        return 0

    # * USE THIS INSTEAD
    def add_server_images(self, images:List, descr:bool = False) -> int:
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
            status=0,
        )




