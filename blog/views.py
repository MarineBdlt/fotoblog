from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, render
from django.shortcuts import get_object_or_404
from django.forms import formset_factory
from django.db.models import Q

from . import forms, models


@login_required
def home(request):
    blogs = models.Blog.objects.filter(
        Q(contributors__in=request.user.follows.all()) | Q(starred=True)
    )
    photos = models.Photo.objects.filter(
        uploader__in=request.user.follows.all()
    ).exclude(blog__in=blogs)
    context = {
        "blogs": blogs,
        "photos": photos,
    }
    return render(request, "blog/home.html", context=context)


@login_required
@permission_required("blog.add_photo", raise_exception=True)
def photo_upload(request):
    form = forms.PhotoForm()
    if request.method == "POST":
        form = forms.PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            # set the uploader to the user before saving the model
            photo.uploader = request.user
            # now we can save
            photo.save()
            return redirect("home")
    return render(request, "blog/photo_upload.html", context={"form": form})


@login_required
@permission_required("blog.create_multiple_photos", raise_exception=True)
def create_multiple_photos(request):
    PhotoFormSet = formset_factory(forms.PhotoForm, extra=5)
    formset = PhotoFormSet()
    if request.method == "POST":
        formset = PhotoFormSet(request.POST, request.FILES)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    photo = form.save(commit=False)
                    photo.uploader = request.user
                    photo.save()
            return redirect("home")
    return render(request, "blog/create_multiple_photos.html", {"formset": formset})


@login_required
@permission_required("blog.add_blog", raise_exception=True)
def blog_create(request):
    blog_form = forms.BlogForm()
    photo_form = forms.PhotoForm()
    if request.method == "POST":
        blog_form = forms.BlogForm(request.POST)
        photo_form = forms.PhotoForm(request.POST, request.FILES)

        if all([blog_form.is_valid, photo_form.is_valid()]):
            photo = photo_form.save(commit=False)
            photo.uploader = request.user
            photo.save()
            blog = blog_form.save(commit=False)
            blog.author = request.user
            blog.photo = photo
            blog.save()
            blog.contributors.add(
                request.user, through_defaults={"contribution": "Auteur principal"}
            )
            return redirect("home")

    context = {
        "blog_form": blog_form,
        "photo_form": photo_form,
    }
    return render(request, "blog/blog_create.html", context=context)


@login_required
def view_blog(request, blog_id):
    blog = get_object_or_404(models.Blog, id=blog_id)
    return render(request, "blog/view_blog.html", {"blog": blog})


@login_required
@permission_required("blog.change_blog", raise_exception=True)
def change_blog(request, blog_id):
    blog = get_object_or_404(models.Blog, id=blog_id)
    edit_form = forms.BlogForm(instance=blog)
    delete_form = forms.DeleteBlogForm()
    if request.method == "POST":
        if "change_blog" in request.POST:
            edit_form = forms.BlogForm(request.POST, instance=blog)
            if edit_form.is_valid():
                edit_form.save()
                return redirect("home")
        if "delete_blog" in request.POST:
            delete_form = forms.DeleteBlogForm(request.POST)
            if delete_form.is_valid():
                blog.delete()
                return redirect("home")
    context = {
        "edit_form": edit_form,
        "delete_form": delete_form,
    }
    return render(request, "blog/change_blog.html", context=context)


# blog/forms.py
from django.contrib.auth import get_user_model

User = get_user_model()

# blog/views.py


@login_required
def follow_users(request):
    form = forms.FollowUsersForm(instance=request.user)
    if request.method == "POST":
        form = forms.FollowUsersForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("home")
    return render(request, "blog/follow_users.html", context={"form": form})
