import json
import os

from django.shortcuts import render

from djangoTest import models


def index(request):
    """
    Site index
    """

    word, created = models.Word.objects.get_or_create(term='Hello')
    word = json.loads(os.environ.get('db_creds'))

    context = {'word': word['username']}

    template = 'index.html'

    return render(
        request,
        template,
        context
    )
