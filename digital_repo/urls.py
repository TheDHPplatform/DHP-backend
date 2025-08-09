from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'collections', views.CollectionViewSet)
router.register(r'artworks', views.ArtworkViewSet)
router.register(r'exhibitions', views.ExhibitionViewSet)
router.register(r'artists', views.ArtistViewSet)

# Library routes
router.register(r'library/document-types', views.DocumentTypeViewSet)
router.register(r'library/subjects', views.SubjectViewSet)
router.register(r'library/publishers', views.PublisherViewSet)
router.register(r'library/authors', views.AuthorViewSet)
router.register(r'library/documents', views.LibraryDocumentViewSet)
router.register(r'library/collections', views.LibraryCollectionViewSet)
router.register(r'library/reading-lists', views.ReadingListViewSet)
router.register(r'library/reviews', views.DocumentReviewViewSet)

# Museum routes
router.register(r'museums/categories', views.MuseumCategoryViewSet)
router.register(r'museums/exhibitions', views.MuseumExhibitionViewSet)
router.register(r'museums/reviews', views.MuseumReviewViewSet)
router.register(r'museums/collections', views.MuseumCollectionViewSet)

# Museum content management routes
router.register(r'museums/sections', views.MuseumSectionViewSet)
router.register(r'museums/gallery', views.MuseumGalleryItemViewSet)
router.register(r'museums/artifacts', views.MuseumArtifactViewSet)
router.register(r'museums/virtual-exhibitions', views.MuseumVirtualExhibitionViewSet)
router.register(r'museums/info', views.MuseumInfoViewSet)
router.register(r'museums', views.MuseumViewSet)

# Archive routes
router.register(r'archives/types', views.ArchiveTypeViewSet)
router.register(r'archives', views.ArchiveViewSet)

# Digital Content routes
router.register(r'digital-content/types', views.DigitalContentTypeViewSet)
router.register(r'digital-content', views.DigitalContentViewSet)

urlpatterns = [
    path('user/content/', views.user_content_overview, name='user-content-overview'),
    path('admin/statistics/', views.admin_statistics_overview, name='admin-statistics-overview'),
] + router.urls