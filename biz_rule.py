from core.models import (Service, Field, Object, CharacterForm, TextForm, IntegerForm, FloatForm, BooleanForm, DateForm,
                         URLForm)
import requests


def main():
    """
    Presumptions:
        > Each pokemon card should be an Object
        > A Field object needs creating for each attribute of a pokemon card
        > A Form object needs creating for each Field and Value of the pokemon cards
    """
    # --- delete all services on each run; fresh slate for each new run ---
    services = Service.objects.all()
    for service in services:
        service.delete()

    # Service the overall name of what we're getting?
    pokemon_service = Service.objects.create(name="Pokemon Cards", description="cards")

    request = requests.get("https://api.pokemontcg.io/v1/cards").json()

    # --- dynamically create fields based on first card available ---
    first_card = request.get("cards")[0]
    field_type_dict = {
        str: "TEXT",
        int: "INTEGER",
        float: "FLOAT",
        bool: "BOOLEAN",
        list: "TEXT"
    }

    for field_name, field_val in first_card.items():
        field_type = type(field_val)
        create_field_type = field_type_dict.get(field_type)
        if field_type is str:
            # handle if string is a URL (could have imported URL validation model but wasn't sure so added basic check)
            if "url" in field_name.lower() and "https://" in field_val:
                create_field_type = "URL"

        new_field = Field.objects.get(
            service=pokemon_service, name=field_name, description=field_name + " desc", form_type=create_field_type
        )

    # --- now create object for each card entry, and a Form object for each available field ---

    # dictionary used to get specific Form model needed per field type
    field_type_to_forms = {
        "CHAR": CharacterForm,
        "TEXT": TextForm,
        "INTEGER": IntegerForm,
        "FLOAT": FloatForm,
        "BOOLEAN": BooleanForm,
        "DATE": DateForm,
        "URL": URLForm
    }

    all_fields = Field.objects.filter(service=pokemon_service)
    for card in request.get("cards"):
        new_obj = Object.objects.create(service=pokemon_service)
        for field in all_fields:
            card_val = card.get(field.name)

            # could maybe add something here to handle if values should be CHAR rather than TEXT?
            # and perhaps format the fields that are lists of strings and dicts a little better?

            new_form = field_type_to_forms.get(field.form_type).objects.get(
                value=card_val, object=new_obj, field=field
            )


