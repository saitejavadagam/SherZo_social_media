from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Profile, Post, LikePost, FollowersCount
from django.contrib.auth.decorators import login_required
from itertools import chain

# Create your views here.

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user)
    user_profile = Profile.objects.get(user=request.user)

    users_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        users_following_list.append(users.user)

    for usernames in users_following_list:
        feed.append(Post.objects.filter(user=usernames))

    feed_list = list(chain(*feed))

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': feed_list})


@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if request.FILES.get('image') is None:
            image = user_profile.profileImg
        else:
            image = request.FILES.get('image')

        bio = request.POST['bio']
        location = request.POST['location']

        user_profile.profileImg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.save()

        return redirect('settings')

    return render(request, 'setting.html', {'user_profile': user_profile})


@login_required(login_url='signin')
def upload(request):
    if request.method == "POST":
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, caption=caption, image=image)
        new_post.save()

        return redirect('/')

    else:
        return redirect('/')


@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    post_id = request.GET['post-id']
    post = Post.objects.get(id=post_id)
    like_filer = LikePost.objects.filter(username=username, post_id=post_id).first()

    if like_filer is None:
        new_like = LikePost.objects.create(username=username, post_id=post_id)
        new_like.save()

        post.no_of_likes += 1
        post.save()
    else:
        like_filer.delete()
        post.no_of_likes -= 1
        post.save()

    return redirect('/')


@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(user=pk,follower=follower).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    follower_count = len(FollowersCount.objects.filter(user=pk))
    following_count = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'follower_count': follower_count,
        'following_count': following_count,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def follow(request):

    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            FollowersCount.objects.get(follower=follower, user=user).delete()
            return redirect('/profile/'+user)
        else:
            FollowersCount.objects.create(follower=follower, user=user).save()
            return redirect('/profile/'+user)

    else:
        return redirect('/')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already registered.')
                return redirect('signup')

            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already registered.')
                return redirect('signup')

            else:
                user = User.objects.create_user(username, email, password)
                user.save()

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')

        else:
            messages.info(request, 'Passwords do not match')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username or password incorrect')
            return redirect('signin')

    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')
