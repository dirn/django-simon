from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django_simon import get_object_or_404

from polls.models import Poll


def index(request):
    latest_poll_list = Poll.find(pub_date__lte=timezone.now()) \
        .sort('-pub_date').limit(5)
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'polls/index.html', context)


def detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, pub_date__lte=timezone.now())
    return render(request, 'polls/detail.html', {'poll': poll})


def results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id, pub_date__lte=timezone.now())
    return render(request, 'polls/results.html', {'poll': poll})


def vote(request, poll_id):
    p = get_object_or_404(Poll, id=poll_id, pub_date__lte=timezone.now())

    if 'choice' in request.POST:
        index = 0
        for choice in p.choices:
            if choice['choice_text'] == request.POST['choice']:
                p.raw_update({'$inc': {'choices.{0}.votes'.format(index): 1}})
                return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))
            index += 1
    return render(request, 'polls/detail.html', {
        'poll': p,
        'error_message': "You didn't select a choice.",
    })
