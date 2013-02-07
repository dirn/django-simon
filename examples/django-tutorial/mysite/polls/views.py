from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django_simon import get_object_or_404

from polls.models import Poll


def index(request):
    latest_poll_list = Poll.all().sort('-pub_date').limit(5)
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'polls/index.html', context)


def detail(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, 'polls/detail.html', {'poll': poll})


def results(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    return render(request, 'polls/results.html', {'poll': poll})


def vote(request, poll_id):
    p = get_object_or_404(Poll, id=poll_id)

    index = 0
    for choice in p.choices:
        if choice.choice_text == request.POST['choice']:
            p.raw_update({'$inc': {'choices.{0}.votes'.format(index): 1}})
            break
        index += 1
    if index == len(p.choices):
        return render(request, 'polls/detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })

    return HttpResponseRedirect(reverse('results', args=(p.id,)))
