from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from PIL import Image
import os

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Collection(models.Model):
    COLLECTION_TYPES = [
        ('gallery', 'Art Gallery'),
        ('museum', 'Museum'),
        ('library', 'Library'),
        ('archive', 'Archive'),
        ('digital', 'Digital Content'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    collection_type = models.CharField(max_length=20, choices=COLLECTION_TYPES)
    description = models.TextField()
    curator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='curated_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class DocumentType(models.Model):
    """Categories for library documents"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Subject(models.Model):
    """Academic subjects for categorizing documents"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Publisher(models.Model):
    """Publishers for books and documents"""
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='publishers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Author(models.Model):
    """Authors for library documents"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    bio = models.TextField(blank=True)
    birth_year = models.IntegerField(blank=True, null=True)
    death_year = models.IntegerField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='authors/', blank=True, null=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class LibraryDocument(models.Model):
    """Main model for library documents (books, papers, etc.)"""
    DOCUMENT_TYPES = [
        ('book', 'Book'),
        ('research_paper', 'Research Paper'),
        ('journal_article', 'Journal Article'),
        ('thesis', 'Thesis'),
        ('report', 'Report'),
        ('manual', 'Manual'),
        ('magazine', 'Magazine'),
        ('newspaper', 'Newspaper'),
        ('other', 'Other'),
    ]
    
    ACCESS_LEVELS = [
        ('public', 'Public'),
        ('restricted', 'Restricted'),
        ('private', 'Private'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, blank=True)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    
    # Document Details
    document_type = models.ForeignKey(DocumentType, on_delete=models.CASCADE, related_name='documents')
    authors = models.JSONField(default=list, blank=True, help_text="List of author names")
    subjects = models.JSONField(default=list, blank=True, help_text="List of subject names")
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    
    # Publication Details
    isbn = models.CharField(max_length=20, blank=True, help_text="ISBN for books")
    doi = models.CharField(max_length=200, blank=True, help_text="DOI for academic papers")
    publication_date = models.DateField(blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True)
    volume = models.CharField(max_length=50, blank=True)
    issue = models.CharField(max_length=50, blank=True)
    pages = models.CharField(max_length=50, blank=True)
    
    # Language and Tags
    language = models.CharField(max_length=50, default='English')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    keywords = models.CharField(max_length=500, blank=True, help_text="Academic keywords")
    
    # Files and Media
    cover_image = models.ImageField(upload_to='library/covers/', blank=True, null=True)
    document_file = models.FileField(upload_to='library/documents/', blank=True, null=True)
    preview_file = models.FileField(upload_to='library/previews/', blank=True, null=True)
    
    # Access and Visibility
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='public')
    is_featured = models.BooleanField(default=False)
    is_downloadable = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    file_size = models.BigIntegerField(blank=True, null=True, help_text="File size in bytes")
    page_count = models.PositiveIntegerField(blank=True, null=True)
    reading_time_minutes = models.PositiveIntegerField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_documents')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_authors_display(self):
        if isinstance(self.authors, list):
            return ", ".join(self.authors)
        return ""
    
    def get_subjects_display(self):
        if isinstance(self.subjects, list):
            return ", ".join(self.subjects)
        return ""
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document_type', 'access_level']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['is_featured', 'access_level']),
        ]

class LibraryCollection(models.Model):
    """Collections of library documents"""
    COLLECTION_TYPES = [
        ('curated', 'Curated Collection'),
        ('series', 'Book Series'),
        ('conference', 'Conference Proceedings'),
        ('journal', 'Journal Issue'),
        ('special', 'Special Collection'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    collection_type = models.CharField(max_length=20, choices=COLLECTION_TYPES, default='curated')
    documents = models.ManyToManyField(LibraryDocument, related_name='collections')
    cover_image = models.ImageField(upload_to='library/collections/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='library_collections')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def document_count(self):
        return self.documents.count()
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class ReadingList(models.Model):
    """User reading lists"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_lists')
    documents = models.ManyToManyField(LibraryDocument, related_name='reading_lists')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user.username}-{self.name}")
        super().save(*args, **kwargs)
    
    def document_count(self):
        return self.documents.count()
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

class DocumentReview(models.Model):
    """Reviews and ratings for library documents"""
    document = models.ForeignKey(LibraryDocument, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    review = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.document.title} ({self.rating}/5)"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['document', 'user']

class Artist(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    bio = models.TextField(blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Artwork(models.Model):
    ARTWORK_TYPES = [
        ('painting', 'Painting'),
        ('sculpture', 'Sculpture'),
        ('photography', 'Photography'),
        ('digital', 'Digital Art'),
        ('traditional_dance', 'Traditional Dance'),
        ('handicraft', 'Handicraft'),
        ('landscape', 'Landscape'),
        ('historical', 'Historical Art'),
        ('performance', 'Performance'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artworks', null=True, blank=True)
    artist_name = models.CharField(max_length=200, help_text="Alternative to artist field for non-registered artists")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='artworks')
    # collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='artworks')
    artwork_type = models.CharField(max_length=20, choices=ARTWORK_TYPES)
    
    # Content fields
    description = models.TextField()
    image = models.ImageField(upload_to='artworks/%Y/%m/')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/', blank=True)
    
    # Metadata
    year_created = models.IntegerField(null=True, blank=True)
    medium = models.CharField(max_length=200, blank=True)
    dimensions = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Tags and keywords
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    cultural_significance = models.TextField(blank=True)
    
    # Administrative fields
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_artworks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_public']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        super().save(*args, **kwargs)
        
        # Generate thumbnail if doesn't exist
        if self.image and not self.thumbnail:
            self.create_thumbnail()
    
    def create_thumbnail(self):
        if self.image:
            img = Image.open(self.image.path)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            # Create thumbnail path
            thumb_name = f"thumb_{os.path.basename(self.image.name)}"
            thumb_path = os.path.join(os.path.dirname(self.image.path), thumb_name)
            img.save(thumb_path)
            
            # Update thumbnail field
            self.thumbnail.name = f"thumbnails/{thumb_name}"
            super().save(update_fields=['thumbnail'])
    
    def get_artist_display(self):
        return self.artist.name if self.artist else self.artist_name
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
    
    def __str__(self):
        return self.title

class Exhibition(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    artworks = models.ManyToManyField(Artwork, related_name='exhibitions')
    curator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exhibitions')
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    is_virtual = models.BooleanField(default=False)
    
    poster_image = models.ImageField(upload_to='exhibitions/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        from django.utils import timezone
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    USER_TYPES = [
        ('visitor', 'Visitor'),
        ('contributor', 'Contributor'),
        ('curator', 'Curator'),
        ('admin', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='visitor')
    bio = models.TextField(blank=True)
    organization = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en')
    email_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


# Museum Models
class MuseumCategory(models.Model):
    """Categories for museums (Historical, Cultural, Art, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    color = models.CharField(max_length=7, default='#6B7280', help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Museum Categories"
        ordering = ['name']


class Museum(models.Model):
    """Museum model with all necessary information"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('maintenance', 'Under Maintenance'),
        ('closed', 'Temporarily Closed'),
        ('archived', 'Archived'),
    ]
    
    ACCESS_LEVELS = [
        ('public', 'Public'),
        ('restricted', 'Restricted Access'),
        ('private', 'Private'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(help_text="Short description for listing")
    long_description = models.TextField(help_text="Detailed description for museum page")
    
    # Location and Contact
    location = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Rwanda')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Categorization
    category = models.ForeignKey(MuseumCategory, on_delete=models.CASCADE, related_name='museums')
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    # Media
    main_image = models.ImageField(upload_to='museums/main/', help_text="Primary museum image")
    gallery_images = models.JSONField(default=list, blank=True, help_text="List of additional image URLs")
    virtual_tour_url = models.URLField(blank=True, help_text="URL for virtual tour")
    video_url = models.URLField(blank=True, help_text="YouTube or Vimeo video URL")
    
    # Operational Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='public')
    opening_hours = models.JSONField(default=dict, blank=True, help_text="Opening hours by day")
    admission_fee = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    admission_info = models.TextField(blank=True, help_text="Admission requirements and pricing details")
    
    # Features and Amenities
    has_parking = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)
    has_restaurant = models.BooleanField(default=False)
    has_gift_shop = models.BooleanField(default=False)
    is_wheelchair_accessible = models.BooleanField(default=False)
    has_guided_tours = models.BooleanField(default=False)
    
    # Statistics and Metadata
    established_year = models.IntegerField(blank=True, null=True)
    visitor_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, 
                               validators=[MinValueValidator(0), MaxValueValidator(5)])
    review_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    # Administrative
    curator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='curated_museums')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_museums')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def increment_visitor_count(self):
        self.visitor_count += 1
        self.save(update_fields=['visitor_count'])
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_average_rating(self):
        reviews = self.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'status']),
            models.Index(fields=['location', 'status']),
            models.Index(fields=['is_featured', 'status']),
        ]


class MuseumExhibition(models.Model):
    """Exhibitions within museums"""
    EXHIBITION_TYPES = [
        ('permanent', 'Permanent Exhibition'),
        ('temporary', 'Temporary Exhibition'),
        ('special', 'Special Exhibition'),
        ('traveling', 'Traveling Exhibition'),
    ]
    
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name='exhibitions')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    exhibition_type = models.CharField(max_length=20, choices=EXHIBITION_TYPES)
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    
    # Media
    poster_image = models.ImageField(upload_to='exhibitions/', blank=True, null=True)
    gallery_images = models.JSONField(default=list, blank=True)
    
    # Information
    curator_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.museum.slug}-{self.title}")
            self.slug = base_slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.museum.name}"
    
    class Meta:
        ordering = ['-start_date']


class MuseumReview(models.Model):
    """Reviews and ratings for museums"""
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='museum_reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    review_text = models.TextField(blank=True)
    visit_date = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.museum.name} - {self.rating} stars by {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['museum', 'user']  # One review per user per museum


class MuseumCollection(models.Model):
    """Collections of museums for themed groupings"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    museums = models.ManyToManyField(Museum, related_name='museum_collections')
    cover_image = models.ImageField(upload_to='museum_collections/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    curator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class ArchiveType(models.Model):
    """Types of archives like Historical Documents, Government Records, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Archive(models.Model):
    """Archive items that link to external sources"""
    ACCESS_LEVELS = [
        ('public', 'Public'),
        ('restricted', 'Restricted'),
        ('private', 'Private'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('under_review', 'Under Review'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    archive_type = models.ForeignKey(ArchiveType, on_delete=models.CASCADE, related_name='archives')
    external_url = models.URLField(help_text="Link to the external archive source")
    thumbnail_url = models.URLField(blank=True, null=True, help_text="URL to thumbnail image")
    source_institution = models.CharField(max_length=200, help_text="Institution that owns/hosts this archive")
    date_created = models.DateField(blank=True, null=True, help_text="Original creation date of the archived material")
    language = models.CharField(max_length=50, default='en')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='public')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    view_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_archives')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


class DigitalContentType(models.Model):
    """Types of digital content like Datasets, Multimedia, etc."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class DigitalContent(models.Model):
    """Digital content items that link to external sources"""
    ACCESS_LEVELS = [
        ('public', 'Public'),
        ('restricted', 'Restricted'),
        ('private', 'Private'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('under_review', 'Under Review'),
    ]
    
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    content_type = models.ForeignKey(DigitalContentType, on_delete=models.CASCADE, related_name='digital_contents')
    external_url = models.URLField(help_text="Link to the external content source")
    thumbnail_url = models.URLField(blank=True, null=True, help_text="URL to thumbnail image")
    source_organization = models.CharField(max_length=200, help_text="Organization that provides this content")
    license = models.CharField(max_length=100, blank=True, help_text="License information")
    format_type = models.CharField(max_length=50, blank=True, help_text="File format or content format")
    size = models.CharField(max_length=50, blank=True, help_text="Size of the content (file size, dataset size, etc.)")
    language = models.CharField(max_length=50, default='en')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='public')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    view_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_digital_contents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()] if self.tags else []
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']


# New models for museum content management
class MuseumSection(models.Model):
    """Sections of content for museum detail pages"""
    SECTION_TYPES = [
        ('overview', 'Overview'),
        ('cultural-heritage', 'Cultural Heritage'),
        ('natural-history', 'Natural History'),
        ('history', 'History'),
        ('exhibitions', 'Exhibitions'),
        ('custom', 'Custom Section'),
    ]
    
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name='sections')
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    title = models.CharField(max_length=200)
    content = models.JSONField(default=list, help_text="List of content paragraphs")
    subsections = models.JSONField(default=list, blank=True, help_text="List of subsection objects")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.museum.name} - {self.title}"
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['museum', 'section_type']


class MuseumGalleryItem(models.Model):
    """Gallery images for museums"""
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name='gallery_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='museums/gallery/')
    image_url = models.URLField(blank=True, help_text="Alternative to uploaded image")
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url
    
    def __str__(self):
        return f"{self.museum.name} - {self.title}"
    
    class Meta:
        ordering = ['order', 'created_at']


class MuseumArtifact(models.Model):
    """Artifacts and items displayed in museums"""
    ARTIFACT_CATEGORIES = [
        ('royal-regalia', 'Royal Regalia'),
        ('ceremonial-weapons', 'Ceremonial Weapons'),
        ('musical-instruments', 'Musical Instruments'),
        ('domestic-items', 'Domestic Items'),
        ('religious-objects', 'Religious Objects'),
        ('artwork', 'Artwork'),
        ('tools', 'Tools'),
        ('textiles', 'Textiles'),
        ('jewelry', 'Jewelry'),
        ('pottery', 'Pottery'),
        ('other', 'Other'),
    ]
    
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name='artifacts')
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=ARTIFACT_CATEGORIES)
    historical_period = models.CharField(max_length=100, blank=True)
    origin = models.CharField(max_length=200, blank=True)
    materials = models.CharField(max_length=200, blank=True, help_text="Materials used to create the artifact")
    dimensions = models.CharField(max_length=100, blank=True, help_text="Size/dimensions of the artifact")
    image = models.ImageField(upload_to='museums/artifacts/', blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="Alternative to uploaded image")
    is_on_display = models.BooleanField(default=True)
    acquisition_date = models.DateField(blank=True, null=True)
    acquisition_method = models.CharField(max_length=100, blank=True, help_text="How the artifact was acquired")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_image_url(self):
        if self.image:
            return self.image.url
        return self.image_url
    
    def __str__(self):
        return f"{self.museum.name} - {self.name}"
    
    class Meta:
        ordering = ['order', 'created_at']


class MuseumVirtualExhibition(models.Model):
    """Virtual exhibitions and digital experiences for museums"""
    EXHIBITION_TYPES = [
        ('tour', 'Virtual Tour'),
        ('experience', '360° Experience'),
        ('exhibition', 'Digital Exhibition'),
        ('interactive', 'Interactive Experience'),
        ('documentary', 'Documentary'),
        ('audio-guide', 'Audio Guide'),
    ]
    
    museum = models.ForeignKey(Museum, on_delete=models.CASCADE, related_name='virtual_exhibitions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    exhibition_type = models.CharField(max_length=20, choices=EXHIBITION_TYPES)
    url = models.URLField(help_text="URL to the virtual exhibition/experience")
    thumbnail_image = models.ImageField(upload_to='museums/virtual_exhibitions/', blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, help_text="Alternative to uploaded thumbnail")
    duration = models.CharField(max_length=50, blank=True, help_text="Estimated duration (e.g., '45 minutes')")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    requires_registration = models.BooleanField(default=False)
    access_instructions = models.TextField(blank=True, help_text="Instructions for accessing the virtual exhibition")
    technical_requirements = models.TextField(blank=True, help_text="Technical requirements (VR headset, etc.)")
    order = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_thumbnail_url(self):
        if self.thumbnail_image:
            return self.thumbnail_image.url
        return self.thumbnail_url
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def __str__(self):
        return f"{self.museum.name} - {self.title}"
    
    class Meta:
        ordering = ['order', 'created_at']


class MuseumInfo(models.Model):
    """Additional operational information for museums"""
    museum = models.OneToOneField(Museum, on_delete=models.CASCADE, related_name='additional_info')
    hours = models.CharField(max_length=200, default="9:00 AM - 5:00 PM")
    contact = models.CharField(max_length=200, blank=True)
    admission = models.TextField(blank=True, help_text="Admission pricing and details")
    facilities = models.JSONField(default=list, help_text="List of available facilities")
    directions = models.TextField(blank=True, help_text="Directions to the museum")
    parking_info = models.TextField(blank=True)
    accessibility_info = models.TextField(blank=True)
    group_booking_info = models.TextField(blank=True)
    special_programs = models.JSONField(default=list, help_text="List of special programs offered")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.museum.name} - Additional Info"
    
    class Meta:
        verbose_name = "Museum Additional Information"
        verbose_name_plural = "Museum Additional Information"
