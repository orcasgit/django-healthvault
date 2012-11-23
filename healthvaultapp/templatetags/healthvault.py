from django import template

from healthvaultapp import utils


register = template.Library()


@register.filter
def is_integrated_with_healthvault(user):
    """Return ``True`` if we have integration info for the user.

    For example::

        {% if request.user|is_integrated_with_healthvault %}
            You're integrated with HealthVault!
        {% else %}
            Would you like to integrate with HealthVault?
        {% endif %}
    """
    return utils.is_integrated(user)
