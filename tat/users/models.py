import django.db.models as models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CharField, IntegerField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for tat."""

    class Types(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        ADMIN = "ADMIN", "Admin"

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    type = models.CharField(
        _("Type"), max_length=64, choices=Types.choices, default=Types.NORMAL
    )
    html_table_context_before = IntegerField(
        default=10, validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    html_table_context_after = IntegerField(
        default=0, validators=[MaxValueValidator(100), MinValueValidator(0)]
    )

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
