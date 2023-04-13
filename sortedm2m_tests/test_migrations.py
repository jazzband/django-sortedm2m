from django.db import migrations, models

from sortedm2m.fields import SortedManyToManyField
from sortedm2m.operations import AlterSortedManyToManyField

from .test_base import OperationTestBase


class OperationTests(OperationTestBase):

    available_apps = ["example.testapp"]
    databases = {'default'}

    def test_alter_field_m2m(self):
        project_state = self.set_up_test_model("test_alflmm", second_model=True)

        project_state = self.apply_operations(
            "test_alflmm",
            project_state,
            operations=[
                migrations.AddField(
                    "Pony",
                    "stables",
                    models.ManyToManyField("Stable", related_name="ponies"),
                )
            ],
        )
        Pony = project_state.apps.get_model("test_alflmm", "Pony")
        self.assertFalse(Pony._meta.get_field("stables").blank)

        with self.assertRaises(TypeError):
            self.apply_operations(
                "test_alflmm",
                project_state,
                operations=[
                    AlterSortedManyToManyField(
                        "Pony",
                        "stables",
                        models.ManyToManyField(
                            to="Stable", related_name="ponies", blank=True
                        ),
                    )
                ],
            )

    def test_alter_field_m2m_to_sorted(self):
        project_state = self.set_up_test_model("test_alflmm", second_model=True)
        Pony = project_state.apps.get_model("test_alflmm", "Pony")

        project_state = self.apply_operations(
            "test_alflmm",
            project_state,
            operations=[
                migrations.AddField(
                    "Pony",
                    "stables",
                    models.ManyToManyField("Stable", related_name="ponies"),
                )
            ],
        )
        Pony = project_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), models.ManyToManyField)

        # Create data to check after migration
        pony = Pony.objects.create(weight=2.5)
        Stable = project_state.apps.get_model("test_alflmm", "Stable")
        pony.stables.add(
            Stable.objects.create(),
            Stable.objects.create()
        )

        project_state = self.apply_operations(
            "test_alflmm",
            project_state,
            operations=[
                AlterSortedManyToManyField(
                    "Pony",
                    "stables",
                    SortedManyToManyField(
                        to="Stable", related_name="ponies", blank=True
                    ),
                )
            ],
        )
        Pony = project_state.apps.get_model("test_alflmm", "Pony")
        pony = Pony.objects.first()
        assert len(set(pony.stables.all())) == 2
        self.assertIsInstance(Pony._meta.get_field("stables"), SortedManyToManyField)

    def test_alter_field_sortedm2m_to_m2m(self):
        project_state = self.set_up_test_model("test_alflmm", second_model=True)

        project_state = self.apply_operations(
            "test_alflmm",
            project_state,
            operations=[
                migrations.AddField(
                    "Pony",
                    "stables",
                    SortedManyToManyField("Stable", related_name="ponies"),
                )
            ],
        )
        Pony = project_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), SortedManyToManyField)

        # Create data to check after migration
        pony = Pony.objects.create(weight=2.5)
        Stable = project_state.apps.get_model("test_alflmm", "Stable")
        pony.stables.add(
            Stable.objects.create(),
            Stable.objects.create()
        )
        stable_ids = [stable.id for stable in pony.stables.all()]

        project_state = self.apply_operations(
            "test_alflmm",
            project_state,
            operations=[
                AlterSortedManyToManyField(
                    "Pony",
                    "stables",
                    models.ManyToManyField(
                        to="Stable", related_name="ponies", blank=True
                    ),
                )
            ],
        )
        Pony = project_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), models.ManyToManyField)

        # Check that data is still there and ordered
        pony = Pony.objects.first()
        assert [stable.id for stable in pony.stables.all()] == stable_ids

    def test_unapply_alter_field_m2m_to_sortedm2m(self):
        project_state = self.set_up_test_model("test_alflmm", second_model=True)

        project_state = self.apply_operations(
            "test_alflmm",
            project_state,
            operations=[
                migrations.AddField(
                    "Pony",
                    "stables",
                    models.ManyToManyField("Stable", related_name="ponies"),
                )
            ],
        )
        Pony = project_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), models.ManyToManyField)

        new_state = project_state.clone()

        new_state = self.apply_operations(
            "test_alflmm",
            new_state,
            operations=[
                AlterSortedManyToManyField(
                    "Pony",
                    "stables",
                    SortedManyToManyField(
                        to="Stable", related_name="ponies", blank=True
                    ),
                )
            ],
        )
        Pony = new_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), SortedManyToManyField)

        original_state = self.unapply_operations(
            "test_alflmm",
            project_state,
            operations=[
                AlterSortedManyToManyField(
                    "Pony",
                    "stables",
                    SortedManyToManyField(
                        to="Stable", related_name="ponies", blank=True
                    ),
                )
            ],
        )
        Pony = original_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), models.ManyToManyField)

    def test_unapply_alter_field_sortedm2m_to_m2m(self):
        project_state = self.set_up_test_model("test_alflmm", second_model=True)

        project_state = self.apply_operations(
            "test_alflmm",
            project_state,
            operations=[
                migrations.AddField(
                    "Pony",
                    "stables",
                    SortedManyToManyField("Stable", related_name="ponies"),
                )
            ],
        )
        Pony = project_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), SortedManyToManyField)

        new_state = project_state.clone()

        new_state = self.apply_operations(
            "test_alflmm",
            new_state,
            operations=[
                AlterSortedManyToManyField(
                    "Pony",
                    "stables",
                    models.ManyToManyField(
                        to="Stable", related_name="ponies", blank=True
                    ),
                )
            ],
        )
        Pony = new_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), models.ManyToManyField)

        original_state = self.unapply_operations(
            "test_alflmm",
            project_state,
            operations=[
                AlterSortedManyToManyField(
                    "Pony",
                    "stables",
                    models.ManyToManyField(
                        to="Stable", related_name="ponies", blank=True
                    ),
                )
            ],
        )
        Pony = original_state.apps.get_model("test_alflmm", "Pony")
        self.assertIsInstance(Pony._meta.get_field("stables"), SortedManyToManyField)
