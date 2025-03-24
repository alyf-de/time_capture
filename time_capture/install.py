from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

from .custom_fields import get_custom_fields
from .property_setters import get_property_setters
from .utils import make_property_setters
from time_capture.patches.set_mandatory_breaks import set_mandatory_breaks


def after_install():
	create_custom_fields(get_custom_fields())
	make_property_setters(get_property_setters())
	set_mandatory_breaks()
