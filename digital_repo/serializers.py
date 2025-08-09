from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    artwork_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = '__all__'

# Library Serializers
class DocumentTypeSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()
    
    def get_document_count(self, obj):
        return obj.documents.count()
    
    class Meta:
        model = DocumentType
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    def get_document_count(self, obj):
        return obj.documents.count()
    
    def get_children(self, obj):
        if obj.children.exists():
            return SubjectSerializer(obj.children.all(), many=True).data
        return []
    
    class Meta:
        model = Subject
        fields = '__all__'

class PublisherSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()
    
    def get_document_count(self, obj):
        return obj.documents.count()
    
    class Meta:
        model = Publisher
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()
    
    def get_document_count(self, obj):
        return obj.documents.count()
    
    class Meta:
        model = Author
        fields = '__all__'

class LibraryDocumentSerializer(serializers.ModelSerializer):
    authors_display = serializers.CharField(source='get_authors_display', read_only=True)
    subjects_display = serializers.CharField(source='get_subjects_display', read_only=True)
    document_type_name = serializers.CharField(source='document_type.name', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    uploaded_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    class Meta:
        model = LibraryDocument
        fields = '__all__'

class LibraryDocumentDetailSerializer(LibraryDocumentSerializer):
    document_type = DocumentTypeSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    collections = serializers.SerializerMethodField()
    
    def get_collections(self, obj):
        return [{'name': collection.name, 'slug': collection.slug} for collection in obj.collections.all()]
    
    class Meta:
        model = LibraryDocument
        fields = '__all__'

class LibraryCollectionSerializer(serializers.ModelSerializer):
    document_count = serializers.CharField(read_only=True)
    collection_type_display = serializers.CharField(source='get_collection_type_display', read_only=True)
    
    class Meta:
        model = LibraryCollection
        fields = '__all__'

class LibraryCollectionDetailSerializer(LibraryCollectionSerializer):
    documents = LibraryDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = LibraryCollection
        fields = '__all__'

class ReadingListSerializer(serializers.ModelSerializer):
    document_count = serializers.CharField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ReadingList
        fields = '__all__'
        read_only_fields = ['user']

class ReadingListDetailSerializer(ReadingListSerializer):
    documents = LibraryDocumentSerializer(many=True, read_only=True)
    
    class Meta:
        model = ReadingList
        fields = '__all__'
        read_only_fields = ['user']

class DocumentReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = DocumentReview
        fields = '__all__'
        read_only_fields = ['user']

class ArtistSerializer(serializers.ModelSerializer):
    artwork_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Artist
        fields = ['id', 'name', 'slug', 'bio', 'birth_year', 'death_year', 
                 'nationality', 'artwork_count']

class CollectionSerializer(serializers.ModelSerializer):
    curator_name = serializers.CharField(source='curator.get_full_name', read_only=True)
    artwork_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Collection
        fields = ['id', 'name', 'slug', 'collection_type', 'description', 
                 'curator_name', 'artwork_count', 'is_featured', 'created_at']
    
    def get_artwork_count(self, obj):
        return obj.artworks.filter(is_public=True).count()

class ArtworkSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    artist_display = serializers.CharField(source='get_artist_display', read_only=True)
    tags_list = serializers.ListField(source='get_tags_list', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    uploaded_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Artwork
        fields = ['id', 'title', 'slug', 'artist_display', 'category_name', 
                 'artwork_type', 'description', 'image', 
                 'thumbnail', 'year_created', 'medium', 'dimensions', 'location',
                 'tags_list', 'cultural_significance', 'uploaded_by_name', 
                 'created_at', 'is_featured', 'view_count', 'uploaded_by', 'category']

class ExhibitionSerializer(serializers.ModelSerializer):
    curator_name = serializers.CharField(source='curator.get_full_name', read_only=True)
    artwork_count = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Exhibition
        fields = ['id', 'title', 'slug', 'description', 'curator_name', 
                 'start_date', 'end_date', 'location', 'is_virtual', 
                 'poster_image', 'artwork_count', 'is_active']
    
    def get_artwork_count(self, obj):
        return obj.artworks.count()


# Museum Serializers
class MuseumCategorySerializer(serializers.ModelSerializer):
    museum_count = serializers.SerializerMethodField()
    
    def get_museum_count(self, obj):
        return obj.museums.filter(status='active').count()
    
    class Meta:
        model = MuseumCategory
        fields = '__all__'


class MuseumSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    curator_name = serializers.CharField(source='curator.get_full_name', read_only=True)
    tags_list = serializers.CharField(source='get_tags_list', read_only=True)
    average_rating = serializers.CharField(source='get_average_rating', read_only=True)
    exhibition_count = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    def get_exhibition_count(self, obj):
        return obj.exhibitions.filter(is_active=True).count()
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()
    
    class Meta:
        model = Museum
        fields = [
            'id', 'name', 'slug', 'description', 'long_description', 'location', 
            'address', 'city', 'country', 'phone', 'email', 'website',
            'category', 'category_name', 'category_slug', 'tags', 'tags_list',
            'main_image', 'gallery_images', 'virtual_tour_url', 'video_url',
            'status', 'opening_hours', 'admission_fee', 'admission_info',
            'has_parking', 'has_wifi', 'has_restaurant', 'has_gift_shop',
            'is_wheelchair_accessible', 'has_guided_tours', 'established_year',
            'visitor_count', 'view_count', 'rating', 'average_rating', 'review_count',
            'is_featured', 'curator', 'curator_name', 'exhibition_count',
            'created_at', 'updated_at'
        ]


class MuseumDetailSerializer(MuseumSerializer):
    category = MuseumCategorySerializer(read_only=True)
    recent_reviews = serializers.SerializerMethodField()
    active_exhibitions = serializers.SerializerMethodField()
    
    def get_recent_reviews(self, obj):
        recent_reviews = obj.reviews.filter(is_approved=True)[:5]
        return MuseumReviewSerializer(recent_reviews, many=True).data
    
    def get_active_exhibitions(self, obj):
        active_exhibitions = obj.exhibitions.filter(is_active=True)[:5]
        return MuseumExhibitionSerializer(active_exhibitions, many=True).data
    
    class Meta(MuseumSerializer.Meta):
        fields = MuseumSerializer.Meta.fields + ['recent_reviews', 'active_exhibitions']


class MuseumExhibitionSerializer(serializers.ModelSerializer):
    museum_name = serializers.CharField(source='museum.name', read_only=True)
    museum_slug = serializers.CharField(source='museum.slug', read_only=True)
    exhibition_type_display = serializers.CharField(source='get_exhibition_type_display', read_only=True)
    
    class Meta:
        model = MuseumExhibition
        fields = '__all__'


class MuseumReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    museum_name = serializers.CharField(source='museum.name', read_only=True)
    
    class Meta:
        model = MuseumReview
        fields = '__all__'
        read_only_fields = ['user', 'helpful_count', 'is_verified']


class MuseumCollectionSerializer(serializers.ModelSerializer):
    museum_count = serializers.SerializerMethodField()
    curator_name = serializers.CharField(source='curator.get_full_name', read_only=True)
    
    def get_museum_count(self, obj):
        return obj.museums.count()
    
    class Meta:
        model = MuseumCollection
        fields = '__all__'


class MuseumCollectionDetailSerializer(MuseumCollectionSerializer):
    museums = MuseumSerializer(many=True, read_only=True)
    
    class Meta(MuseumCollectionSerializer.Meta):
        fields = MuseumCollectionSerializer.Meta.fields


# Archive Serializers
class ArchiveTypeSerializer(serializers.ModelSerializer):
    archive_count = serializers.SerializerMethodField()
    
    def get_archive_count(self, obj):
        return obj.archives.count()
    
    class Meta:
        model = ArchiveType
        fields = '__all__'


class ArchiveSerializer(serializers.ModelSerializer):
    archive_type = ArchiveTypeSerializer(read_only=True)
    archive_type_id = serializers.IntegerField(write_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    tags_list = serializers.SerializerMethodField()
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    class Meta:
        model = Archive
        fields = '__all__'
        read_only_fields = ('slug', 'view_count', 'click_count', 'uploaded_by', 'created_at', 'updated_at')


class ArchiveDetailSerializer(ArchiveSerializer):
    archive_type = ArchiveTypeSerializer(read_only=True)
    
    class Meta(ArchiveSerializer.Meta):
        fields = ArchiveSerializer.Meta.fields


# Digital Content Serializers
class DigitalContentTypeSerializer(serializers.ModelSerializer):
    content_count = serializers.SerializerMethodField()
    
    def get_content_count(self, obj):
        return obj.digital_contents.count()
    
    class Meta:
        model = DigitalContentType
        fields = '__all__'


class DigitalContentSerializer(serializers.ModelSerializer):
    content_type = DigitalContentTypeSerializer(read_only=True)
    content_type_id = serializers.IntegerField(write_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    tags_list = serializers.SerializerMethodField()
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    class Meta:
        model = DigitalContent
        fields = '__all__'
        read_only_fields = ('slug', 'view_count', 'click_count', 'uploaded_by', 'created_at', 'updated_at')


class DigitalContentDetailSerializer(DigitalContentSerializer):
    content_type = DigitalContentTypeSerializer(read_only=True)
    
    class Meta(DigitalContentSerializer.Meta):
        fields = DigitalContentSerializer.Meta.fields


# New serializers for museum content management
class MuseumSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuseumSection
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MuseumGalleryItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    def get_image_url(self, obj):
        return obj.get_image_url()
    
    class Meta:
        model = MuseumGalleryItem
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MuseumArtifactSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    def get_image_url(self, obj):
        return obj.get_image_url()
    
    class Meta:
        model = MuseumArtifact
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class MuseumVirtualExhibitionSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()
    exhibition_type_display = serializers.CharField(source='get_exhibition_type_display', read_only=True)
    
    def get_thumbnail_url(self, obj):
        return obj.get_thumbnail_url()
    
    class Meta:
        model = MuseumVirtualExhibition
        fields = '__all__'
        read_only_fields = ('view_count', 'created_at', 'updated_at')


class MuseumInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuseumInfo
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


# Enhanced Museum Detail Serializer with all content
class MuseumDetailWithContentSerializer(MuseumDetailSerializer):
    sections = MuseumSectionSerializer(many=True, read_only=True)
    gallery_items = MuseumGalleryItemSerializer(many=True, read_only=True)
    artifacts = MuseumArtifactSerializer(many=True, read_only=True)
    virtual_exhibitions = MuseumVirtualExhibitionSerializer(many=True, read_only=True)
    additional_info = MuseumInfoSerializer(read_only=True)
    
    class Meta(MuseumDetailSerializer.Meta):
        fields = MuseumDetailSerializer.Meta.fields + [
            'sections', 'gallery_items', 'artifacts', 'virtual_exhibitions', 'additional_info'
        ]

