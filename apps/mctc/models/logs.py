from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from malnutrition.models import log

from datetime import datetime

# since there's only ever going to be a limited number of message
# on a strict one to one basis, lets just define them here,
# pushing the full text or setting up another model would work too
messages = {
    "provider_registered": _("Provider registered, waiting confirmation"),
    "patient_created": _("Patient created"),
    "muac_taken": _("MUAC taken for the patient"),
    "mrdt_taken": _("MRDT taken for the patient"),
    "diagnosis_taken": _("Diagnosis taken for the patient"),    
    "user_logged_in": _("User logged into the user interface"),
    "confirmed_join": _("Provider confirmed"),
    "case_cancelled": _("Case was cancelled by the provider"),
    "note_added": _("Note added to the case by the provider")    
}

class MessageLog(log.MessageLog):
    """ A wrapper to pull in the app_label """
    class Meta(log.MessageLog.Meta):
        app_label = "mctc"

class EventLog(models.Model):
    """ This is a much more refined log, giving you nicer messages """
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    message = models.CharField(max_length=25, choices=tuple(messages.items()))
    created_at  = models.DateTimeField(db_index=True)

    class Meta:
        app_label = "mctc"
        ordering = ("-created_at",)

    def get_absolute_url(self):
        return self.content_object.get_absolute_url()

def log(source, message):
    if not messages.has_key(message):
        raise ValueError, "No message: %s exists, please add to logs.py"
    if not source.id:
        print "* Cannot log until the object has been saved, id is None, %s" % message
    ev = EventLog()
    ev.content_object = source
    ev.message = message
    ev.created_at = datetime.now()
    ev.save()

