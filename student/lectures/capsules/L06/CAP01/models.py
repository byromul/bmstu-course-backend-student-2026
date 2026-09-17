from django.db import models


class Scenario(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        app_label = "lecture"


class Scene(models.Model):
    id = models.CharField(primary_key=True, max_length=40)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="scenes")
    kind = models.CharField(max_length=20)

    class Meta:
        app_label = "lecture"
