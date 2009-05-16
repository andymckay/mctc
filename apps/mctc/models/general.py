from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

from malnutrition.models import zone, case, facility, provider

class Zone(zone.Zone):
    class Meta(case.Case.Meta):
        app_label = "mctc"
        
class Facility(facility.Facility):
    class Meta(case.Case.Meta):
        app_label = "mctc"

class Provider(provider.Provider):
    class Meta(case.Case.Meta):
        app_label = "mctc"
        
    def get_absolute_url(self):
        return "/provider/view/%s/" % self.id
            
class Case(case.Case):
    """ A generic case or patient table """
    class Meta(case.Case.Meta):
        app_label = "mctc"
        
    def get_absolute_url(self):
        return "/case/%s/" % self.id
            
class CaseNote(models.Model):
    case        = models.ForeignKey("Case", related_name="notes", db_index=True)
    created_by  = models.ForeignKey(User, db_index=True)
    created_at  = models.DateTimeField(auto_now_add=True, db_index=True)
    text        = models.TextField()

    def save(self, *args):
        if not self.id:
            self.created_at = datetime.now()
        super(CaseNote, self).save(*args)

    class Meta:
        app_label = "mctc"