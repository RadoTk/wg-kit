from django.core.management.base import BaseCommand
from django.db import transaction

# Deterministic mapping and validation for Wagtail form field types
ALLOWED_FIELD_TYPES = {
    "singleline",
    "multiline",
    "email",
    "number",
    "url",
    "checkbox",
    "checkboxes",
    "dropdown",
    "multiselect",
    "radio",
    "date",
    "datetime",
    "hidden",
}

# Common invalid → valid mappings. Extend as needed, but keep deterministic.
FIELD_TYPE_MAPPING = {
    "text": "singleline",
    "textarea": "multiline",
    "select": "dropdown",
    "tel": "singleline",
    "phone": "singleline",
    "password": "singleline",
}


class Command(BaseCommand):
    help = (
        "Audit and optionally fix invalid field_type values in app.contact FormField.\n"
        "By default, performs a dry-run showing invalid rows. Use --apply to update them deterministically."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply fixes using FIELD_TYPE_MAPPING; fallback to 'singleline' if no mapping exists.",
        )

    def handle(self, *args, **options):
        from app.contact.models import FormField  # Import inside for deterministic app loading

        qs = FormField.objects.exclude(field_type__in=ALLOWED_FIELD_TYPES).order_by("id")
        count = qs.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No invalid field types found."))
            return

        # Dry-run list
        self.stdout.write("Found %d invalid FormField rows:" % count)
        for f in qs:
            self.stdout.write(
                " - id=%s, label=%r, field_type=%r" % (f.id, f.label, f.field_type)
            )

        if not options.get("apply"):
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run only. Re-run with --apply to update invalid field types."
                )
            )
            return

        # Apply deterministic fixes
        updated = 0
        with transaction.atomic():
            for f in qs:
                fixed = FIELD_TYPE_MAPPING.get(f.field_type, "singleline")
                if fixed not in ALLOWED_FIELD_TYPES:
                    # Defensive guard; should never happen
                    fixed = "singleline"
                f.field_type = fixed
                f.save(update_fields=["field_type"])
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Updated %d FormField rows to valid field types." % updated
            )
        )