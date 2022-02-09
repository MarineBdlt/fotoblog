from django.conf import settings
from django.db import models
from PIL import Image


class Photo(models.Model):
    def __str__(self):
        return f"{self.caption}"

    image = models.ImageField(verbose_name="image")
    caption = models.CharField(max_length=128, blank=True, verbose_name="légende")
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    IMAGE_MAX_SIZE = (800, 800)

    def resize_image(self):
        image = Image.open(self.image)
        image.thumbnail(self.IMAGE_MAX_SIZE)
        # sauvegarde de l’image redimensionnée dans le système de fichiers
        # ce n’est pas la méthode save() du modèle !
        image.save(self.image.path)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.resize_image()


class Blog(models.Model):
    def __str__(self):
        return f"{self.title}"

    photo = models.ForeignKey(Photo, null=True, on_delete=models.SET_NULL, blank=True)
    title = models.CharField(max_length=128, verbose_name="titre")
    content = models.CharField(max_length=5000, verbose_name="contenu")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    starred = models.BooleanField(default=False)
    words_count = models.IntegerField(null=True)

    def _get_word_count(self):
        return len(self.content.split(" "))

    def save(self, *args, **kwargs):
        self.word_count = self._get_word_count()
        super().save(*args, **kwargs)
