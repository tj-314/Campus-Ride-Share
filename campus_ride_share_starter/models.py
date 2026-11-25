from datetime import date
import re

class ValidationError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__("Please correct the listed fields.")

class RidePost:
    @staticmethod
    def validate(data):
        errors = {}
        for field in ("destination", "travel_date", "departure_time", "contact"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                errors[field] = "Required field."
        if data.get("post_type") not in ("offer", "request"):
            errors["post_type"] = "Choose offer or request."
        if "travel_date" not in errors:
            try:
                date.fromisoformat(data["travel_date"])
            except ValueError:
                errors["travel_date"] = "Enter a valid YYYY-MM-DD date."
        if "departure_time" not in errors and not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", data["departure_time"]):
            errors["departure_time"] = "Enter a valid HH:MM time."
        if data.get("post_type") == "offer":
            seat_text = str(data.get("seats", ""))
            if not re.fullmatch(r"[0-9]+", seat_text) or int(seat_text) < 1:
                errors["seats"] = "Enter a whole number of at least 1."
        if errors:
            raise ValidationError(errors)
        return {"post_type": data["post_type"],
                **{k: data[k].strip() for k in ("destination", "travel_date", "departure_time", "contact")},
                "seats": int(data["seats"]) if data["post_type"] == "offer" else None}
