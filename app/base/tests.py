from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission


class SeedUsersCommandTests(TestCase):
    def test_roles_created_and_permissions(self):
        call_command("seed_users")

        # Roles as Groups
        super_admin = Group.objects.get(name="super-admin")
        admin = Group.objects.get(name="admin")
        user_group = Group.objects.get(name="user")

        # super-admin should have all permissions
        self.assertEqual(
            super_admin.permissions.count(), Permission.objects.count()
        )

        # admin should only have view_* permissions
        expected_view_count = Permission.objects.filter(
            codename__startswith="view_"
        ).count()
        self.assertEqual(admin.permissions.count(), expected_view_count)
        self.assertTrue(
            all(p.codename.startswith("view_") for p in admin.permissions.all())
        )

        # user should have no explicit permissions
        self.assertEqual(user_group.permissions.count(), 0)

    def test_users_created_flags_groups_and_passwords(self):
        call_command("seed_users")
        User = get_user_model()

        # super-admins
        sa1 = User.objects.get(username="super-admin1")
        sa2 = User.objects.get(username="super-admin2")
        self.assertTrue(sa1.is_staff)
        self.assertTrue(sa1.is_superuser)
        self.assertTrue(sa2.is_staff)
        self.assertTrue(sa2.is_superuser)
        self.assertTrue(sa1.groups.filter(name="super-admin").exists())
        self.assertTrue(sa2.groups.filter(name="super-admin").exists())
        self.assertTrue(sa1.check_password("motdepasse1"))
        self.assertTrue(sa2.check_password("motdepasse2"))
        self.assertNotEqual(sa1.password, "motdepasse1")
        self.assertNotEqual(sa2.password, "motdepasse2")

        # admins
        a1 = User.objects.get(username="admin1")
        a2 = User.objects.get(username="admin2")
        self.assertTrue(a1.is_staff)
        self.assertFalse(a1.is_superuser)
        self.assertTrue(a2.is_staff)
        self.assertFalse(a2.is_superuser)
        self.assertTrue(a1.groups.filter(name="admin").exists())
        self.assertTrue(a2.groups.filter(name="admin").exists())
        self.assertTrue(a1.check_password("motdepasse1"))
        self.assertTrue(a2.check_password("motdepasse2"))
        self.assertNotEqual(a1.password, "motdepasse1")
        self.assertNotEqual(a2.password, "motdepasse2")

        # users
        u1 = User.objects.get(username="user1")
        u2 = User.objects.get(username="user2")
        self.assertFalse(u1.is_staff)
        self.assertFalse(u1.is_superuser)
        self.assertFalse(u2.is_staff)
        self.assertFalse(u2.is_superuser)
        self.assertTrue(u1.groups.filter(name="user").exists())
        self.assertTrue(u2.groups.filter(name="user").exists())
        self.assertTrue(u1.check_password("motdepasse1"))
        self.assertTrue(u2.check_password("motdepasse2"))
        self.assertNotEqual(u1.password, "motdepasse1")
        self.assertNotEqual(u2.password, "motdepasse2")

    def test_idempotent_rerun(self):
        # First run
        call_command("seed_users")
        User = get_user_model()
        initial_usernames = {
            "super-admin1",
            "super-admin2",
            "admin1",
            "admin2",
            "user1",
            "user2",
        }

        self.assertEqual(User.objects.filter(username__in=initial_usernames).count(), 6)
        self.assertEqual(Group.objects.filter(name__in=["super-admin", "admin", "user"]).count(), 3)

        # Second run should not create duplicates
        call_command("seed_users")
        self.assertEqual(User.objects.filter(username__in=initial_usernames).count(), 6)
        self.assertEqual(Group.objects.filter(name__in=["super-admin", "admin", "user"]).count(), 3)