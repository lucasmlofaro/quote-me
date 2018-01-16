from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render
from django.contrib.auth.models import User
from django.forms import inlineformset_factory

from daily_quote.forms import ProfileEditForm, UserEditForm
from daily_quote.models import Profile, Quote, QuoteRank


def home(request):
    context = {
        'authenticated': request.user.is_authenticated
    }

    if request.user.is_authenticated:
        quote = request.user.profile.recommend().quote
        context['quote'] = quote
        context['rank'] = QuoteRank.objects.get(profile=request.user.profile, quote=quote).rank
    else:
        context['quote'] = Quote.random_quote()
        context['rank'] = 0

    return render(request, 'daily_quote/home.html', context)


def user_profile(request, username):
    context = {
        'my_profile': False,
    }

    try:
        user_edit_form = UserEditForm(instance=request.user)
        profile_edit_form = ProfileEditForm(instance=request.user.profile)

        if request.user.username == username:
            context['my_profile'] = True
            profile = request.user.profile

            if all([user_edit_form.is_valid(), profile_edit_form.is_valid()]):
                user_edit_form.save()
                profile = profile_edit_form.save()
        else:
            profile = Profile.objects.get(user__username=username)

        quoterank = profile.recommend()

        context['profile'] = profile
        context['quote'] = quoterank.quote
        context['rank'] = quoterank.rank
        context['quotes'] = Quote.objects.filter(profile=profile)
        context['user_edit_form'] = user_edit_form
        context['profile_edit_form'] = profile_edit_form

    except Profile.DoesNotExist:
        raise Http404("Profile Does Not Exist")

    return render(request, 'daily_quote/profile.html', context)


def rank_quote(request, rank=0):
    user = request.user
    quote = user.profile.current_quote
    quoterank = QuoteRank.objects.get(profile__user=user, quote=quote)
    quoterank.rank = rank
    quoterank.save()

    context = {
        'my_profile': True,
        'profile': user.profile,
        'quote': quote,
        'rank': rank,
        'quotes': Quote.objects.filter(profile__user=user),
    }

    return render(request, 'daily_quote/profile.html', context)
