from django.db import models
from wagtail.models import ClusterableModel
from wagtail.search import index
from wagtail.models import (Task,TaskState,)
from django.conf import settings
from wagtail.models import (
    DraftStateMixin,
    LockableMixin,
    PreviewableMixin,
    RevisionMixin,
    Task,
    TaskState,
    WorkflowMixin,
)

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    PublishingPanel,
)
from django.contrib.contenttypes.fields import GenericRelation
from wagtail.api import APIField
from django.utils.translation import gettext as _


class Person(
    WorkflowMixin,
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    PreviewableMixin,
    index.Indexed,
    ClusterableModel,
):
    """
    A Django model to store Person objects.
    It is registered using `register_snippet` as a function in wagtail_hooks.py
    to allow it to have a menu item within a custom menu item group.

    `Person` uses the `ClusterableModel`, which allows the relationship with
    another model to be stored locally to the 'parent' model (e.g. a PageModel)
    until the parent is explicitly saved. This allows the editor to use the
    'Preview' button, to preview the content, without saving the relationships
    to the database.
    https://github.com/wagtail/django-modelcluster
    """

    first_name = models.CharField("First name", max_length=254)
    last_name = models.CharField("Last name", max_length=254)
    job_title = models.CharField("Job title", max_length=254)

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    workflow_states = GenericRelation(
        "wagtailcore.WorkflowState",
        content_type_field="base_content_type",
        object_id_field="object_id",
        related_query_name="person",
        for_concrete_model=False,
    )

    revisions = GenericRelation(
        "wagtailcore.Revision",
        content_type_field="base_content_type",
        object_id_field="object_id",
        related_query_name="person",
        for_concrete_model=False,
    )

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("first_name"),
                        FieldPanel("last_name"),
                    ]
                )
            ],
            "Name",
        ),
        FieldPanel("job_title"),
        FieldPanel("image"),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("first_name"),
        index.SearchField("last_name"),
        index.FilterField("job_title"),
        index.AutocompleteField("first_name"),
        index.AutocompleteField("last_name"),
    ]

    api_fields = [
        APIField("first_name"),
        APIField("last_name"),
        APIField("job_title"),
        APIField("image"),
    ]

    @property
    def thumb_image(self):
        # Returns an empty string if there is no profile pic or the rendition
        # file can't be found.
        try:
            return self.image.get_rendition("fill-50x50").img_tag()
        except:  # noqa: E722 FIXME: remove bare 'except:'
            return ""

    @property
    def preview_modes(self):
        return PreviewableMixin.DEFAULT_PREVIEW_MODES + [("blog_post", _("Blog post"))]

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_preview_template(self, request, mode_name):
        from rootapp.blog.models import BlogPage

        if mode_name == "blog_post":
            return BlogPage.template
        return "base/preview/person.html"

    def get_preview_context(self, request, mode_name):
        from rootapp.blog.models import BlogPage

        context = super().get_preview_context(request, mode_name)
        if mode_name == self.default_preview_mode:
            return context

        page = BlogPage.objects.filter(blog_person_relationship__person=self).first()
        if page:
            # Use the page authored by this person if available,
            # and replace the instance from the database with the edited instance
            page.authors = [
                self if author.pk == self.pk else author for author in page.authors()
            ]
            # The authors() method only shows live authors, so make sure the instance
            # is included even if it's not live as this is just a preview
            if not self.live:
                page.authors.append(self)
        else:
            # Otherwise, get the first page and simulate the person as the author
            page = BlogPage.objects.first()
            page.authors = [self]

        context["page"] = page
        return context

    class Meta:
        verbose_name = "person"
        verbose_name_plural = "people"
class UserApprovalTaskState(TaskState):
    pass


class UserApprovalTask(Task):
    """
    Based on https://docs.wagtail.org/en/stable/extending/custom_tasks.html.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=False
    )

    admin_form_fields = Task.admin_form_fields + ["user"]

    task_state_class = UserApprovalTaskState

    # prevent editing of `user` after the task is created
    # by default, this attribute contains the 'name' field to prevent tasks from being renamed
    admin_form_readonly_on_edit_fields = Task.admin_form_readonly_on_edit_fields + [
        "user"
    ]

    def user_can_access_editor(self, page, user):
        return user == self.user

    def page_locked_for_user(self, page, user):
        return user != self.user

    def get_actions(self, page, user):
        if user == self.user:
            return [
                ("approve", "Approve", False),
                ("reject", "Reject", False),
                ("cancel", "Cancel", False),
            ]
        else:
            return []

    def on_action(self, task_state, user, action_name, **kwargs):
        if action_name == "cancel":
            return task_state.workflow_state.cancel(user=user)
        else:
            return super().on_action(task_state, user, action_name, **kwargs)

    def get_task_states_user_can_moderate(self, user, **kwargs):
        if user == self.user:
            # get all task states linked to the (base class of) current task
            return TaskState.objects.filter(
                status=TaskState.STATUS_IN_PROGRESS, task=self.task_ptr
            )
        else:
            return TaskState.objects.none()

    @classmethod
    def get_description(cls):
        return _("Only a specific user can approve this task")
