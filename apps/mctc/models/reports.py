from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from apps.mctc.models.general import Case, Provider

from datetime import datetime
import md5

from malnutrition.models import report

class Observation(report.Observation):
    class Meta(report.Observation.Meta):
        app_label = "mctc"
                
class ReportMalaria(report.Report):
    class Meta:
        get_latest_by = 'entered_at'
        ordering = ("-entered_at",)
        app_label = "mctc"
    
    diagnosis = models.ManyToManyField("Diagnosis")
    bednet = models.BooleanField(db_index=True)
    result = models.BooleanField(db_index=True) 
    observed = models.ManyToManyField(Observation)       

    def get_dictionary(self):
        return {
            'result': self.result,
            'result_text': self.result and "Y" or "N",
            'bednet': self.bednet,
            'bednet_text': self.bednet and "Y" or "N",
            'observed': ", ".join([k.name for k in self.observed.all()]),            
        }
        
        
class ReportMalnutrition(report.ReportMalnutrition):
    # a wrapper around the base malnutrition report
    class Meta(report.ReportMalnutrition.Meta):
        app_label = "mctc"
    
    def diagnose (self):
        complications = [c for c in self.observed.all() if c.uid != "edema"]
        edema = "edema" in [ c.uid for c in self.observed.all() ]
        self.status = ReportMalnutrition.HEALTHY_STATUS
        if edema or self.muac < 110:
            if complications:
                self.status = ReportMalnutrition.SEVERE_COMP_STATUS
            else:
                self.status =  ReportMalnutrition.SEVERE_STATUS
        elif self.muac < 125:
            self.status =  ReportMalnutrition.MODERATE_STATUS

    def get_dictionary(self):
        data = {
            'diagnosis_msg': self.diagnosis_msg(),
        }
        dct = super(ReportMalnutrition, self).get_dictionary()
        dct.update(data)
        return dct

    def diagnosis_msg(self):
        if self.status == ReportMalnutrition.MODERATE_STATUS:
            msg = "MAM Child requires supplemental feeding."
        elif self.status == ReportMalnutrition.SEVERE_STATUS:
            msg = "SAM Patient requires OTP care"
        elif self.status == ReportMalnutrition.SEVERE_COMP_STATUS:
            msg = "SAM+ Patient requires IMMEDIATE inpatient care"
        else:
            msg = "Child is not malnourished"

        return msg

class Lab(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    
    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "mctc"
        ordering = ("code",)        

class LabDiagnosis(models.Model):
    lab = models.ForeignKey(Lab)
    diagnosis = models.ForeignKey("ReportDiagnosis")
    amount = models.IntegerField(blank=True, null=True)
    result = models.BooleanField(blank=True)

    def __unicode__(self):
        return "%s, %s - %s" % (self.lab, self.diagnosis, self.amount)

    class Meta:
        app_label = "mctc"

class DiagnosisCategory(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = "mctc"
        ordering = ("name",)
        
class Diagnosis(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10)
    category = models.ForeignKey(DiagnosisCategory)
    mvp_code = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    
    def __unicode__(self):
        return self.mvp_code

    class Meta:
        app_label = "mctc"
        ordering = ("code",)
        
class ReportDiagnosis(report.Report):
    diagnosis = models.ManyToManyField(Diagnosis)
    lab = models.ManyToManyField(Lab, through=LabDiagnosis)
    text = models.TextField()
    
    def __unicode__(self):
        return self.case

    class Meta:
        verbose_name = "Diagnoses"
        app_label = "mctc"


    def get_dictionary(self):
        extra = []
        for ld in LabDiagnosis.objects.filter(diagnosis=self):
            if ld.amount:
                extra.append("%s %s" % (ld.lab.code, ld.amount))
            else:
                extra.append("%s%s" % (ld.lab.code, ld.result and "+" or "-"))
                
        return {
            "diagnosis": ", ".join([str(d) for d in self.diagnosis.all()]),
            "labs": ", ".join([str(d) for d in self.lab.all()]),
            "labs_text": ", ".join(extra)
        }
