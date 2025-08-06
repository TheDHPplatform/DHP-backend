from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from .models import *
from .serializers import *

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(artwork_count=Count('artworks'))
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['collection_type', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

class ArtworkViewSet(viewsets.ModelViewSet):
    queryset = Artwork.objects.filter(is_public=True)
    serializer_class = ArtworkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'artwork_type', 'is_featured']
    search_fields = ['title', 'description', 'artist_name', 'tags']
    ordering_fields = ['created_at', 'title', 'view_count']
    ordering = ['-created_at']
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured artworks"""
        featured = self.queryset.filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently added artworks"""
        recent = self.queryset.order_by('-created_at')[:12]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular artworks by view count"""
        popular = self.queryset.order_by('-view_count')[:12]
        serializer = self.get_serializer(popular, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search with multiple filters"""
        queryset = self.queryset
        
        # Search query
        q = request.query_params.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(artist_name__icontains=q) |
                Q(tags__icontains=q)
            )
        
        # Category filter
        category = request.query_params.get('category', '')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Year range
        year_from = request.query_params.get('year_from', '')
        year_to = request.query_params.get('year_to', '')
        if year_from:
            queryset = queryset.filter(year_created__gte=year_from)
        if year_to:
            queryset = queryset.filter(year_created__lte=year_to)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ExhibitionViewSet(viewsets.ModelViewSet):
    queryset = Exhibition.objects.all()
    serializer_class = ExhibitionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering = ['-start_date']
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active exhibitions"""
        from django.utils import timezone
        now = timezone.now()
        active = self.queryset.filter(start_date__lte=now, end_date__gte=now)
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artist.objects.annotate(artwork_count=Count('artworks'))
    serializer_class = ArtistSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bio']
    ordering = ['name']

# Library Views
class DocumentTypeViewSet(viewsets.ModelViewSet):
    queryset = DocumentType.objects.all()
    serializer_class = DocumentTypeSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.filter(parent__isnull=True)  # Top-level subjects only
    serializer_class = SubjectSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']

class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['name']

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'bio', 'nationality']
    ordering = ['name']

class LibraryDocumentViewSet(viewsets.ModelViewSet):
    queryset = LibraryDocument.objects.filter(access_level='public')
    serializer_class = LibraryDocumentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'access_level', 'is_featured', 'language', 'publication_year']
    search_fields = ['title', 'subtitle', 'description', 'abstract', 'tags', 'keywords']
    ordering_fields = ['created_at', 'title', 'publication_date', 'view_count', 'download_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LibraryDocumentDetailSerializer
        return self.serializer_class
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured documents"""
        featured = self.queryset.filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently added documents"""
        recent = self.queryset.order_by('-created_at')[:12]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular documents by view count"""
        popular = self.queryset.order_by('-view_count')[:12]
        serializer = self.get_serializer(popular, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def most_downloaded(self, request):
        """Get most downloaded documents"""
        most_downloaded = self.queryset.order_by('-download_count')[:12]
        serializer = self.get_serializer(most_downloaded, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def download(self, request, slug=None):
        """Download a document"""
        document = self.get_object()
        if not document.is_downloadable:
            return Response({'error': 'Document is not downloadable'}, status=status.HTTP_403_FORBIDDEN)
        
        document.increment_download_count()
        return Response({'download_url': document.document_file.url if document.document_file else None})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search with multiple filters"""
        queryset = self.queryset
        
        # Search query
        q = request.query_params.get('q', '')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(abstract__icontains=q) |
                Q(tags__icontains=q) |
                Q(keywords__icontains=q)
            )
        
        # Document type filter
        doc_type = request.query_params.get('document_type', '')
        if doc_type:
            queryset = queryset.filter(document_type__slug=doc_type)
        
        # Subject filter
        subject = request.query_params.get('subject', '')
        if subject:
            queryset = queryset.filter(subjects__contains=[subject])
        
        # Author filter
        author = request.query_params.get('author', '')
        if author:
            queryset = queryset.filter(authors__contains=[author])
        
        # Publisher filter
        publisher = request.query_params.get('publisher', '')
        if publisher:
            queryset = queryset.filter(publisher__slug=publisher)
        
        # Year range
        year_from = request.query_params.get('year_from', '')
        year_to = request.query_params.get('year_to', '')
        if year_from:
            queryset = queryset.filter(publication_year__gte=year_from)
        if year_to:
            queryset = queryset.filter(publication_year__lte=year_to)
        
        # Language filter
        language = request.query_params.get('language', '')
        if language:
            queryset = queryset.filter(language__icontains=language)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class LibraryCollectionViewSet(viewsets.ModelViewSet):
    queryset = LibraryCollection.objects.all()
    serializer_class = LibraryCollectionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['collection_type', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return LibraryCollectionDetailSerializer
        return self.serializer_class
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured collections"""
        featured = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)

class ReadingListViewSet(viewsets.ModelViewSet):
    queryset = ReadingList.objects.all()  # Base queryset for router registration
    serializer_class = ReadingListSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    def get_queryset(self):
        # Users can only see their own reading lists and public ones
        if self.request.user.is_authenticated:
            return ReadingList.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            )
        return ReadingList.objects.filter(is_public=True)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReadingListDetailSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_document(self, request, slug=None):
        """Add a document to the reading list"""
        reading_list = self.get_object()
        if reading_list.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        document_id = request.data.get('document_id')
        try:
            document = LibraryDocument.objects.get(id=document_id)
            reading_list.documents.add(document)
            return Response({'message': 'Document added to reading list'})
        except LibraryDocument.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def remove_document(self, request, slug=None):
        """Remove a document from the reading list"""
        reading_list = self.get_object()
        if reading_list.user != request.user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        document_id = request.data.get('document_id')
        try:
            document = LibraryDocument.objects.get(id=document_id)
            reading_list.documents.remove(document)
            return Response({'message': 'Document removed from reading list'})
        except LibraryDocument.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

class DocumentReviewViewSet(viewsets.ModelViewSet):
    queryset = DocumentReview.objects.all()
    serializer_class = DocumentReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    
    def get_queryset(self):
        document_slug = self.request.query_params.get('document', '')
        if document_slug:
            return DocumentReview.objects.filter(document__slug=document_slug)
        return DocumentReview.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# Museum Views
class MuseumCategoryViewSet(viewsets.ModelViewSet):
    queryset = MuseumCategory.objects.all()
    serializer_class = MuseumCategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class MuseumViewSet(viewsets.ModelViewSet):
    queryset = Museum.objects.filter(status='active')
    serializer_class = MuseumSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'location', 'city', 'is_featured', 'status']
    search_fields = ['name', 'description', 'location', 'tags']
    ordering_fields = ['created_at', 'name', 'view_count', 'rating', 'established_year']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MuseumDetailSerializer
        return MuseumSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured museums"""
        featured = self.queryset.filter(is_featured=True)[:6]
        serializer = self.get_serializer(featured, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get museums grouped by category"""
        categories = MuseumCategory.objects.all()
        result = []
        for category in categories:
            museums = self.queryset.filter(category=category)[:4]
            if museums:
                result.append({
                    'category': MuseumCategorySerializer(category).data,
                    'museums': self.get_serializer(museums, many=True).data
                })
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most popular museums by view count"""
        popular = self.queryset.order_by('-view_count')[:10]
        serializer = self.get_serializer(popular, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently added museums"""
        recent = self.queryset.order_by('-created_at')[:10]
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def visit(self, request, slug=None):
        """Increment visitor count"""
        museum = self.get_object()
        museum.increment_visitor_count()
        return Response({'status': 'visit recorded'})


class MuseumExhibitionViewSet(viewsets.ModelViewSet):
    queryset = MuseumExhibition.objects.filter(is_active=True)
    serializer_class = MuseumExhibitionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['museum', 'exhibition_type', 'is_featured']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']
    
    def get_queryset(self):
        museum_slug = self.request.query_params.get('museum', '')
        if museum_slug:
            return self.queryset.filter(museum__slug=museum_slug)
        return self.queryset
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current exhibitions"""
        from django.utils import timezone
        current_date = timezone.now().date()
        current = self.queryset.filter(
            start_date__lte=current_date,
            end_date__gte=current_date
        ) | self.queryset.filter(
            start_date__lte=current_date,
            end_date__isnull=True,
            exhibition_type='permanent'
        )
        serializer = self.get_serializer(current, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming exhibitions"""
        from django.utils import timezone
        upcoming = self.queryset.filter(start_date__gt=timezone.now().date())
        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)


class MuseumReviewViewSet(viewsets.ModelViewSet):
    queryset = MuseumReview.objects.filter(is_approved=True)
    serializer_class = MuseumReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['museum', 'rating', 'is_verified']
    search_fields = ['title', 'review_text']
    ordering_fields = ['created_at', 'rating', 'helpful_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        museum_slug = self.request.query_params.get('museum', '')
        if museum_slug:
            return self.queryset.filter(museum__slug=museum_slug)
        return self.queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def helpful(self, request, pk=None):
        """Mark review as helpful"""
        review = self.get_object()
        review.helpful_count += 1
        review.save()
        return Response({'status': 'marked as helpful'})


class MuseumCollectionViewSet(viewsets.ModelViewSet):
    queryset = MuseumCollection.objects.all()
    serializer_class = MuseumCollectionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MuseumCollectionDetailSerializer
        return MuseumCollectionSerializer


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, timedelta

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_content_overview(request):
    """Get overview of all content uploaded by the current user"""
    user = request.user
    
    # Get user's artworks
    user_artworks = Artwork.objects.filter(uploaded_by=user)
    artworks_data = []
    for artwork in user_artworks:
        artworks_data.append({
            'id': str(artwork.id),
            'title': artwork.title,
            'type': 'artwork',
            'thumbnail': request.build_absolute_uri(artwork.image.url) if artwork.image else None,
            'description': artwork.description,
            'created_at': artwork.created_at.isoformat(),
            'updated_at': artwork.updated_at.isoformat(),
            'status': 'published' if artwork.is_public else 'private',
            'views': artwork.view_count,
            'downloads': 0,  # Artworks don't have download tracking
            'likes': 0,  # Would need to implement likes system
            'comments': 0,  # Would need to implement comments system
            'category': artwork.category.name if artwork.category else '',
            'tags': artwork.get_tags_list(),
            'access_level': 'public' if artwork.is_public else 'private'
        })
    
    # Get user's library documents
    user_documents = LibraryDocument.objects.filter(uploaded_by=user)
    documents_data = []
    for doc in user_documents:
        documents_data.append({
            'id': str(doc.id),
            'title': doc.title,
            'type': 'document',
            'thumbnail': request.build_absolute_uri(doc.cover_image.url) if doc.cover_image else None,
            'description': doc.description,
            'created_at': doc.created_at.isoformat(),
            'updated_at': doc.updated_at.isoformat(),
            'status': 'published',
            'views': doc.view_count,
            'downloads': doc.download_count,
            'likes': 0,  # Would need to implement likes system
            'comments': 0,  # Would need to implement comments system
            'category': doc.document_type.name if doc.document_type else '',
            'tags': [tag.strip() for tag in doc.tags.split(',') if tag.strip()] if doc.tags else [],
            'file_size': doc.file_size,
            'access_level': doc.access_level
        })
    
    # Get user's museums
    user_museums = Museum.objects.filter(created_by=user)
    museums_data = []
    for museum in user_museums:
        museums_data.append({
            'id': str(museum.id),
            'title': museum.name,
            'type': 'museum',
            'thumbnail': request.build_absolute_uri(museum.main_image.url) if museum.main_image else None,
            'description': museum.description,
            'created_at': museum.created_at.isoformat(),
            'updated_at': museum.updated_at.isoformat(),
            'status': museum.status,
            'views': museum.view_count,
            'downloads': 0,  # Museums don't have downloads
            'likes': 0,  # Would need to implement likes system
            'comments': museum.review_count,
            'category': museum.category.name if museum.category else '',
            'tags': museum.get_tags_list(),
            'access_level': museum.access_level
        })
    
    # Get user's collections
    user_collections = Collection.objects.filter(curator=user)
    collections_data = []
    for collection in user_collections:
        collections_data.append({
            'id': str(collection.id),
            'title': collection.name,
            'type': 'collection',
            'thumbnail': None,  # Collections don't have thumbnails in current model
            'description': collection.description,
            'created_at': collection.created_at.isoformat(),
            'updated_at': collection.updated_at.isoformat(),
            'status': 'published',
            'views': 0,  # Collections don't have view tracking
            'downloads': 0,
            'likes': 0,
            'comments': 0,
            'category': collection.get_collection_type_display(),
            'tags': [],
            'access_level': 'public'
        })
    
    # Combine all content
    all_content = artworks_data + documents_data + museums_data + collections_data
    
    # Calculate totals
    total_views = sum(item['views'] for item in all_content)
    total_downloads = sum(item['downloads'] for item in all_content)
    total_likes = sum(item['likes'] for item in all_content)
    total_comments = sum(item['comments'] for item in all_content)
    
    return Response({
        'content': all_content,
        'stats': {
            'total_items': len(all_content),
            'total_views': total_views,
            'total_downloads': total_downloads,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'by_type': {
                'artworks': len(artworks_data),
                'documents': len(documents_data),
                'museums': len(museums_data),
                'collections': len(collections_data)
            }
        }
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_statistics_overview(request):
    """Get comprehensive statistics for admin dashboard"""
    
    # Calculate date ranges
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)
    
    # User Statistics
    total_users = User.objects.count()
    active_users_today = User.objects.filter(last_login__date=today).count()
    active_users_week = User.objects.filter(last_login__gte=week_ago).count()
    active_users_month = User.objects.filter(last_login__gte=month_ago).count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
    new_users_month = User.objects.filter(date_joined__gte=month_ago).count()
    
    # Content Statistics
    # Artworks
    total_artworks = Artwork.objects.count()
    public_artworks = Artwork.objects.filter(is_public=True).count()
    private_artworks = total_artworks - public_artworks
    featured_artworks = Artwork.objects.filter(is_featured=True).count()
    artworks_today = Artwork.objects.filter(created_at__date=today).count()
    artworks_week = Artwork.objects.filter(created_at__gte=week_ago).count()
    artworks_month = Artwork.objects.filter(created_at__gte=month_ago).count()
    total_artwork_views = Artwork.objects.aggregate(total_views=Sum('view_count'))['total_views'] or 0
    
    # Documents
    total_documents = LibraryDocument.objects.count()
    public_documents = LibraryDocument.objects.filter(access_level='public').count()
    restricted_documents = LibraryDocument.objects.filter(access_level='restricted').count()
    private_documents = LibraryDocument.objects.filter(access_level='private').count()
    featured_documents = LibraryDocument.objects.filter(is_featured=True).count()
    downloadable_documents = LibraryDocument.objects.filter(is_downloadable=True).count()
    documents_today = LibraryDocument.objects.filter(created_at__date=today).count()
    documents_week = LibraryDocument.objects.filter(created_at__gte=week_ago).count()
    documents_month = LibraryDocument.objects.filter(created_at__gte=month_ago).count()
    total_document_views = LibraryDocument.objects.aggregate(total_views=Sum('view_count'))['total_views'] or 0
    total_document_downloads = LibraryDocument.objects.aggregate(total_downloads=Sum('download_count'))['total_downloads'] or 0
    
    # Museums
    total_museums = Museum.objects.count()
    active_museums = Museum.objects.filter(status='active').count()
    featured_museums = Museum.objects.filter(is_featured=True).count()
    museums_today = Museum.objects.filter(created_at__date=today).count()
    museums_week = Museum.objects.filter(created_at__gte=week_ago).count()
    museums_month = Museum.objects.filter(created_at__gte=month_ago).count()
    total_museum_views = Museum.objects.aggregate(total_views=Sum('view_count'))['total_views'] or 0
    total_museum_visitors = Museum.objects.aggregate(total_visitors=Sum('visitor_count'))['total_visitors'] or 0
    
    # Collections
    total_collections = Collection.objects.count()
    featured_collections = Collection.objects.filter(is_featured=True).count()
    collections_today = Collection.objects.filter(created_at__date=today).count()
    collections_week = Collection.objects.filter(created_at__gte=week_ago).count()
    collections_month = Collection.objects.filter(created_at__gte=month_ago).count()
    
    # Library Collections
    total_library_collections = LibraryCollection.objects.count()
    featured_library_collections = LibraryCollection.objects.filter(is_featured=True).count()
    
    # Categories and Types
    total_categories = Category.objects.count()
    total_document_types = DocumentType.objects.count()
    total_museum_categories = MuseumCategory.objects.count()
    total_subjects = Subject.objects.count()
    total_authors = Author.objects.count()
    total_publishers = Publisher.objects.count()
    
    # Reviews and Engagement
    total_document_reviews = DocumentReview.objects.count()
    total_museum_reviews = MuseumReview.objects.count()
    avg_document_rating = DocumentReview.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    avg_museum_rating = MuseumReview.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
    
    # Reading Lists
    total_reading_lists = ReadingList.objects.count()
    public_reading_lists = ReadingList.objects.filter(is_public=True).count()
    private_reading_lists = total_reading_lists - public_reading_lists
    
    # Exhibitions
    total_exhibitions = Exhibition.objects.count()
    total_museum_exhibitions = MuseumExhibition.objects.count()
    active_exhibitions = Exhibition.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).count()
    active_museum_exhibitions = MuseumExhibition.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        is_active=True
    ).count()
    
    # Top Performers
    top_viewed_artworks = Artwork.objects.order_by('-view_count')[:5].values('title', 'view_count', 'slug')
    top_viewed_documents = LibraryDocument.objects.order_by('-view_count')[:5].values('title', 'view_count', 'slug')
    top_downloaded_documents = LibraryDocument.objects.order_by('-download_count')[:5].values('title', 'download_count', 'slug')
    top_viewed_museums = Museum.objects.order_by('-view_count')[:5].values('name', 'view_count', 'slug')
    
    # Top contributors - calculate based on actual uploads
    top_contributors = []
    users_with_uploads = User.objects.annotate(
        artwork_count=Count('uploaded_artworks'),
        document_count=Count('uploaded_documents'),
        museum_count=Count('created_museums')
    ).filter(
        artwork_count__gt=0
    ).union(
        User.objects.annotate(
            artwork_count=Count('uploaded_artworks'),
            document_count=Count('uploaded_documents'),
            museum_count=Count('created_museums')
        ).filter(document_count__gt=0)
    ).union(
        User.objects.annotate(
            artwork_count=Count('uploaded_artworks'),
            document_count=Count('uploaded_documents'),
            museum_count=Count('created_museums')
        ).filter(museum_count__gt=0)
    )
    
    for user in users_with_uploads[:5]:
        artwork_count = user.uploaded_artworks.count()
        document_count = user.uploaded_documents.count()
        museum_count = user.created_museums.count()
        total_uploads = artwork_count + document_count + museum_count
        
        top_contributors.append({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'total_uploads': total_uploads,
            'artworks': artwork_count,
            'documents': document_count,
            'museums': museum_count
        })
    
    # Content by category/type
    artworks_by_category = list(Category.objects.annotate(
        artwork_count=Count('artworks')
    ).values('name', 'artwork_count').order_by('-artwork_count')[:10])
    
    documents_by_type = list(DocumentType.objects.annotate(
        document_count=Count('documents')
    ).values('name', 'document_count').order_by('-document_count')[:10])
    
    museums_by_category = list(MuseumCategory.objects.annotate(
        museum_count=Count('museums')
    ).values('name', 'museum_count').order_by('-museum_count')[:10])
    
    # Growth trends (last 12 months)
    monthly_stats = []
    for i in range(12):
        month_start = (now - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        monthly_stats.append({
            'month': month_start.strftime('%Y-%m'),
            'users': User.objects.filter(date_joined__range=[month_start, month_end]).count(),
            'artworks': Artwork.objects.filter(created_at__range=[month_start, month_end]).count(),
            'documents': LibraryDocument.objects.filter(created_at__range=[month_start, month_end]).count(),
            'museums': Museum.objects.filter(created_at__range=[month_start, month_end]).count(),
        })
    
    monthly_stats.reverse()  # Show oldest to newest
    
    return Response({
        'overview': {
            'total_users': total_users,
            'total_content_items': total_artworks + total_documents + total_museums + total_collections,
            'total_views': total_artwork_views + total_document_views + total_museum_views,
            'total_downloads': total_document_downloads,
            'total_visitors': total_museum_visitors,
            'generated_at': now.isoformat()
        },
        'users': {
            'total': total_users,
            'active_today': active_users_today,
            'active_this_week': active_users_week,
            'active_this_month': active_users_month,
            'new_today': new_users_today,
            'new_this_week': new_users_week,
            'new_this_month': new_users_month,
            'top_contributors': top_contributors
        },
        'content': {
            'artworks': {
                'total': total_artworks,
                'public': public_artworks,
                'private': private_artworks,
                'featured': featured_artworks,
                'added_today': artworks_today,
                'added_this_week': artworks_week,
                'added_this_month': artworks_month,
                'total_views': total_artwork_views,
                'by_category': artworks_by_category,
                'top_viewed': list(top_viewed_artworks)
            },
            'documents': {
                'total': total_documents,
                'public': public_documents,
                'restricted': restricted_documents,
                'private': private_documents,
                'featured': featured_documents,
                'downloadable': downloadable_documents,
                'added_today': documents_today,
                'added_this_week': documents_week,
                'added_this_month': documents_month,
                'total_views': total_document_views,
                'total_downloads': total_document_downloads,
                'by_type': documents_by_type,
                'top_viewed': list(top_viewed_documents),
                'top_downloaded': list(top_downloaded_documents)
            },
            'museums': {
                'total': total_museums,
                'active': active_museums,
                'featured': featured_museums,
                'added_today': museums_today,
                'added_this_week': museums_week,
                'added_this_month': museums_month,
                'total_views': total_museum_views,
                'total_visitors': total_museum_visitors,
                'by_category': museums_by_category,
                'top_viewed': list(top_viewed_museums)
            },
            'collections': {
                'total': total_collections,
                'featured': featured_collections,
                'added_today': collections_today,
                'added_this_week': collections_week,
                'added_this_month': collections_month
            },
            'library_collections': {
                'total': total_library_collections,
                'featured': featured_library_collections
            }
        },
        'metadata': {
            'categories': total_categories,
            'document_types': total_document_types,
            'museum_categories': total_museum_categories,
            'subjects': total_subjects,
            'authors': total_authors,
            'publishers': total_publishers
        },
        'engagement': {
            'document_reviews': {
                'total': total_document_reviews,
                'average_rating': round(avg_document_rating, 2)
            },
            'museum_reviews': {
                'total': total_museum_reviews,
                'average_rating': round(avg_museum_rating, 2)
            },
            'reading_lists': {
                'total': total_reading_lists,
                'public': public_reading_lists,
                'private': private_reading_lists
            }
        },
        'exhibitions': {
            'total_exhibitions': total_exhibitions,
            'total_museum_exhibitions': total_museum_exhibitions,
            'active_exhibitions': active_exhibitions,
            'active_museum_exhibitions': active_museum_exhibitions
        },
        'growth_trends': monthly_stats
    })


# Archive ViewSets
class ArchiveTypeViewSet(viewsets.ModelViewSet):
    queryset = ArchiveType.objects.annotate(archive_count=Count('archives'))
    serializer_class = ArchiveTypeSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ArchiveViewSet(viewsets.ModelViewSet):
    queryset = Archive.objects.filter(status='active')
    serializer_class = ArchiveSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['archive_type', 'access_level', 'status', 'language']
    search_fields = ['title', 'description', 'source_institution', 'tags']
    ordering_fields = ['created_at', 'title', 'view_count', 'click_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ArchiveDetailSerializer
        return ArchiveSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
                
        # Filter by access level based on user authentication
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(access_level='public')
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def track_click(self, request, slug=None):
        """Track external link clicks"""
        archive = self.get_object()
        archive.click_count += 1
        archive.save(update_fields=['click_count'])
        return Response({'message': 'Click tracked successfully'})
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get archives grouped by type"""
        archive_type_slug = request.query_params.get('type')
        if not archive_type_slug:
            return Response({'error': 'Type parameter is required'}, status=400)
        
        try:
            archive_type = ArchiveType.objects.get(slug=archive_type_slug)
            archives = self.get_queryset().filter(archive_type=archive_type)
            serializer = self.get_serializer(archives, many=True)
            return Response({
                'archive_type': ArchiveTypeSerializer(archive_type).data,
                'archives': serializer.data
            })
        except ArchiveType.DoesNotExist:
            return Response({'error': 'Archive type not found'}, status=404)


# Digital Content ViewSets
class DigitalContentTypeViewSet(viewsets.ModelViewSet):
    queryset = DigitalContentType.objects.annotate(content_count=Count('digital_contents'))
    serializer_class = DigitalContentTypeSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class DigitalContentViewSet(viewsets.ModelViewSet):
    queryset = DigitalContent.objects.filter(status='active')
    serializer_class = DigitalContentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['content_type', 'access_level', 'status', 'language', 'format_type']
    search_fields = ['title', 'description', 'source_organization', 'tags']
    ordering_fields = ['created_at', 'title', 'view_count', 'click_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DigitalContentDetailSerializer
        return DigitalContentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by content type name if provided
        content_type_name = self.request.query_params.get('type')
        if content_type_name:
            queryset = queryset.filter(content_type__name__icontains=content_type_name)
        
        # Filter by access level based on user authentication
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(access_level='public')
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def track_click(self, request, slug=None):
        """Track external link clicks"""
        content = self.get_object()
        content.click_count += 1
        content.save(update_fields=['click_count'])
        return Response({'message': 'Click tracked successfully'})
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get digital content grouped by type"""
        content_type_slug = request.query_params.get('type')
        if not content_type_slug:
            return Response({'error': 'Type parameter is required'}, status=400)
        
        try:
            content_type = DigitalContentType.objects.get(slug=content_type_slug)
            contents = self.get_queryset().filter(content_type=content_type)
            serializer = self.get_serializer(contents, many=True)
            return Response({
                'content_type': DigitalContentTypeSerializer(content_type).data,
                'contents': serializer.data
            })
        except DigitalContentType.DoesNotExist:
            return Response({'error': 'Content type not found'}, status=404)
