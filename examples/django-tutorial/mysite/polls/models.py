import datetime

from django.utils import timezone
from django_simon import Model, simonize

simonize()


class Poll(Model):
    class Meta:
        required_fields = ('question', 'pub_date')

    def __unicode__(self):
        return self.question

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now
