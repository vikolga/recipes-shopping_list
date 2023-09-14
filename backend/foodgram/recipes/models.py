from django.db import models

# Create your models here.
class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True
    )
    color = models.CharField(
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True
    )

    class Meta:
        #ordering = ['name',]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color'],
                name='unique_tagcolor'
            ),
        ]

    def __str__(self) -> str:
        return self.name
