from rest_framework.routers import DefaultRouter

from tasks.apps import TasksConfig
from tasks.views import TaskViewSet

app_name = TasksConfig.name

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = router.urls
