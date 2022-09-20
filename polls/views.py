from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.shortcuts import redirect 
from .models import Choice, Question, Vote
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
        pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(LoginRequiredMixin, generic.DetailView):
    """Class based view for viewing a poll."""
    model = Question
    template_name = 'polls/detail.html'
    
    def get(self, request, *args, **kwargs):
        """Check if the question can be voted."""
        user = request.user
        try:
            question = get_object_or_404(Question, pk=kwargs['pk'])
        except Http404:
            messages.error(request, "This question is not available for voting.")
            return HttpResponseRedirect(reverse('polls:index'))
        
        try:
            if not user.is_authenticated:
                raise Vote.DoesNotExist
            user_vote = question.vote_set.get(user=user).choice
        except Vote.DoesNotExist:
            # if user didnt select a choice or invalid cho[ice
            # it will render as didnt select a choice
            return super().get(request, *args, **kwargs)
        else:
            # go to polls detail application
            return render(request, 'polls/detail.html', {
                'question': question,
                'user_vote': user_vote,
            })
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.html', context)

# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

# def results(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/results.html', {'question': question})

@login_required
def vote(request, question_id):
    """Vote for a choice on a question (poll)."""
    user = request.user
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
            
    except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
            })
    else:
        if question.can_vote():
            try:
                user_vote = question.vote_set.get(user=user)
                user_vote.choice = selected_choice
                user_vote.save()
            except Vote.DoesNotExist:
                Vote.objects.create(user=user, choice=selected_choice, question=selected_choice.question).save()
        else:
            messages.error(request, "You can't vote this question.")
            return HttpResponseRedirect(reverse('polls:index'))
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # form.save()
            # username = form.cleaned_data.get('username')
            # raw_passwd = form.cleaned_data.get('password')
            # user = authenticate(username=username, password=raw_passwd)
            user = form.save()
            login(request, user)
            return redirect('/polls')
        # what if form is not valid?
        # we should display a message in signup.html
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form':form})