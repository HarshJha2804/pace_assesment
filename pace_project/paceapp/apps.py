from django.apps import AppConfig


class PaceappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pace_project.paceapp'

    def ready(self):
        import pace_project.paceapp.signals
        from actstream import registry
        AssessmentDiscovery = self.get_model('AssessmentDiscovery')
        from pace_project.users.models import Student
        from pace_project.core.models.application_models import Application
        from pace_project.core.models.core_models import StatusType
        registry.register(Student)
        registry.register(AssessmentDiscovery)
        registry.register(Application)
        registry.register(StatusType)
