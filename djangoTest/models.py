from django.db import models


class Word(models.Model):
    term = models.CharField(max_length=255, db_index=True, unique=True)

    def __str__(self):
        return self.term
