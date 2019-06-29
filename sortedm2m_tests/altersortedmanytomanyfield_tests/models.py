"""See ./migrations/ directory for history of these models.

State after 0001_initial:

    class M2MtoSortedM2M(models.Model):
        m2m = models.ManyToManyField('Target')

    class SortedM2MToM2M(models.Model):
        m2m = SortedManyToManyField('Target')

State after 0002_alter_m2m_fields.py

    class M2MToSortedM2M(models.Model):
        m2m = SortedManyToManyField('Target')

    class SortedM2MToM2M(models.Model):
        m2m = models.ManyToManyField('Target')
"""

from django.db import models

from sortedm2m.fields import SortedManyToManyField


class Target(models.Model):
    pass


class M2MToSortedM2M(models.Model):
    """Test model for migration ManyToManyField -> SortedManyToManyField."""

    m2m = SortedManyToManyField('Target')


class SortedM2MToM2M(models.Model):
    """Test model for migration SortedManyToManyField -> ManyToManyField."""

    m2m = models.ManyToManyField('Target')
