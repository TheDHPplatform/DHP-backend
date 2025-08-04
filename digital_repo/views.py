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
            queryset = queryset.filter(subjects__slug=subject)
        
        # Author filter
        author = request.query_params.get('author', '')
        if author:
            queryset = queryset.filter(authors__slug=author)
        
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
