# # tours/views.py
# from django.utils.decorators import method_decorator
# from django.views.decorators.cache import cache_page
# from rest_framework import viewsets, mixins, permissions, status
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from rest_framework_simplejwt.authentication import JWTAuthentication
#
# from .models import Guide, Tour, Offer, TourParticipant
# from .permissions import IsAdminOrOrganizerOwnerOrReadOnly, IsOrganizerOrAdmin, IsGuideSelf
# from .serializers import GuideSerializer, TourSerializer, OfferSerializer, ParticipantSerializer, \
#     TourGuideAssignmentSerializer
# from rest_framework.exceptions import PermissionDenied
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
#
# from django.utils import timezone
#
# from .models import TourGuideAssignment, Tour
# from .serializers import TourGuideAssignmentSerializer
#
#
# class GuideViewSet(viewsets.ModelViewSet):
#     authentication_classes = [JWTAuthentication]
#     queryset = Guide.objects.all()
#     serializer_class = GuideSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#
# class TourViewSet(viewsets.ModelViewSet):
#     """
#     - Admins → Full CRUD on all tours
#     - Organizers → Full CRUD on their tours
#     - Tourists → Read-only
#     """
#     authentication_classes = [JWTAuthentication]
#     serializer_class = TourSerializer
#     permission_classes = [IsAdminOrOrganizerOwnerOrReadOnly]
#
#     def get_queryset(self):
#         user = self.request.user
#
#         if not user.is_authenticated or user.role == 'tourist':
#             # Tourists and guests can see all tours
#             return Tour.objects.all().order_by('-start_date')
#
#         if user.role == 'organizer':
#             # Organizers see only their tours
#             return Tour.objects.filter(organizer=user).order_by('-start_date')
#
#         # Admin sees all tours
#         return Tour.objects.all().order_by('-start_date')
#
#     def perform_create(self, serializer):
#         # Only organizers or admins can create
#         if self.request.user.role not in ['organizer', 'admin']:
#             raise PermissionDenied("Only organizers or admins can create tours.")
#         serializer.save(organizer=self.request.user)
#
#     @method_decorator(cache_page(60 * 5))  # 5 min cache for list
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)
#
#     @action(detail=True, methods=['get'], url_path='guides', permission_classes=[IsAuthenticated])
#     def guides(self, request, pk=None):
#         tour = get_object_or_404(Tour, pk=pk)
#         assignments = TourGuideAssignment.objects.filter(tour=tour)
#         serializer = TourGuideAssignmentSerializer(assignments, many=True)
#         return Response(serializer.data)
#
#
# class TourGuideAssignmentViewSet(viewsets.GenericViewSet,
#                                  mixins.ListModelMixin,
#                                  mixins.DestroyModelMixin,
#                                  mixins.UpdateModelMixin):
#     serializer_class = TourGuideAssignmentSerializer
#     authentication_classes = [JWTAuthentication]
#
#     def get_queryset(self):
#         user = self.request.user
#         if user.role == 'admin':
#             return TourGuideAssignment.objects.all()
#         elif user.role == 'organizer':
#             return TourGuideAssignment.objects.filter(tour__organizer=user)
#         elif user.role == 'guide':
#             return TourGuideAssignment.objects.filter(guide__user=user)
#         return TourGuideAssignment.objects.none()
#
#     def get_permissions(self):
#         if self.action == 'respond':
#             permission_classes = [IsAuthenticated, IsGuideSelf]
#         elif self.action in ['assign_guide', 'list', 'destroy']:
#             permission_classes = [IsAuthenticated, IsAdminOrOrganizerOwnerOrReadOnly]
#         elif self.action == 'partial_update':  # admin override
#             permission_classes = [IsAdminUser]
#         else:
#             permission_classes = [IsAuthenticated]
#         return [perm() for perm in permission_classes]
#
#     @action(detail=True, methods=['post'], url_path='assign-guide')
#     def assign_guide(self, request, pk=None):
#         user = request.user
#         tour = get_object_or_404(Tour, pk=pk)
#         if not (user.role == 'admin' or (user.role == 'organizer' and tour.organizer == user)):
#             return Response({'detail': 'Not authorized to assign guides.'}, status=403)
#
#         guide_ids = request.data.get('guide_ids')
#         if not guide_ids or not isinstance(guide_ids, list):
#             return Response({'detail': 'guide_ids list required.'}, status=400)
#
#         assignments = []
#         for gid in guide_ids:
#             guide = Guide.objects.filter(id=gid).first()
#             if not guide:
#                 continue
#             # Skip duplicates
#             if TourGuideAssignment.objects.filter(tour=tour, guide=guide, status__in=['pending', 'accepted']).exists():
#                 continue
#             assignment = TourGuideAssignment.objects.create(tour=tour, guide=guide, status='pending')
#             assignments.append(assignment)
#
#         serializer = self.get_serializer(assignments, many=True)
#         return Response(serializer.data, status=201)
#
#     @action(detail=True, methods=['post'], url_path='respond')
#     def respond(self, request, pk=None):
#         assignment = self.get_object()
#         user = request.user
#         if not (user.role == 'guide' and assignment.guide.user == user):
#             return Response({'detail': 'Not authorized to respond.'}, status=403)
#
#         new_status = request.data.get('status')
#         if new_status not in ['accepted', 'declined']:
#             return Response({'detail': 'Invalid status.'}, status=400)
#
#         assignment.status = new_status
#         assignment.save()
#         return Response(self.get_serializer(assignment).data)
#
#     def destroy(self, request, pk=None):
#         assignment = self.get_object()
#         user = request.user
#         if not (user.role == 'admin' or (user.role == 'organizer' and assignment.tour.organizer == user)):
#             return Response({'detail': 'Not authorized to cancel.'}, status=403)
#
#         if assignment.status != 'pending':
#             return Response({'detail': 'Only pending assignments can be cancelled.'}, status=400)
#
#         assignment.delete()
#         return Response(status=204)
#
#
# class OfferViewSet(viewsets.ModelViewSet):
#     """
#     - Admins/Organizers → Full CRUD
#     - Tourists → Read-only
#     """
#     queryset = Offer.objects.all()
#     serializer_class = OfferSerializer
#     permission_classes = [IsAdminOrOrganizerOwnerOrReadOnly]
#
#
# class TourParticipantViewSet(viewsets.ModelViewSet):
#     queryset = TourParticipant.objects.all()
#     serializer_class = ParticipantSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         if user.role == 'admin':
#             return TourParticipant.objects.all()
#         elif user.role == 'organizer':
#             # Only participants for organizer’s tours
#             return TourParticipant.objects.filter(tour__organizer=user)
#         else:
#             # Tourist: See only their participations
#             return TourParticipant.objects.filter(user=user)
#
#     def perform_create(self, serializer):
#         """
#         Tourist joins a tour -> pending by default
#         """
#         user = self.request.user
#         if user.role != 'tourist':
#             raise permissions.PermissionDenied("Only tourists can join tours.")
#         serializer.save(user=user, status='pending')
#
#     # Organizer/Admin Approve Participant
#     @action(detail=True, methods=['patch'], url_path='approve')
#     def approve_participant(self, request, pk=None):
#         participant = self.get_object()
#         if request.user.role not in ['admin', 'organizer']:
#             return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
#
#         participant.status = 'approved'
#         participant.save()
#         return Response({"detail": "Participant approved."}, status=status.HTTP_200_OK)
#
#     # Organizer/Admin Reject Participant
#     @action(detail=True, methods=['patch'], url_path='reject')
#     def reject_participant(self, request, pk=None):
#         participant = self.get_object()
#         if request.user.role not in ['admin', 'organizer']:
#             return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
#
#         participant.status = 'rejected'
#         participant.save()
#         return Response({"detail": "Participant rejected."}, status=status.HTTP_200_OK)

# tours/views.py
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from rest_framework import serializers
from .models import Guide, Tour, Offer, TourParticipant, TourGuideAssignment, Booking
from accounts.models import User
from .permissions import IsAdminOrOrganizerOwnerOrReadOnly, IsOrganizerOrAdmin, IsGuideSelf
from .serializers import GuideSerializer, TourSerializer, OfferSerializer, ParticipantSerializer, \
    TourGuideAssignmentSerializer, MyTourSerializer, BookingSerializer
from django.utils.timezone import now
from django.core.cache import cache
from django.contrib.sessions.models import Session


# -------------------------
# Guide viewset
# -------------------------
class GuideViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = GuideSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tour_id = self.request.query_params.get("tour_id")
        qs = Guide.objects.all()
        if tour_id:
            try:
                tour = Tour.objects.get(pk=tour_id)
            except Tour.DoesNotExist:
                return qs.none()

            # Users who are already assigned to conflicting tours
            conflicting_user_ids = TourGuideAssignment.objects.filter(
                status="accepted",
                tour__start_date__lt=tour.end_date,
                tour__end_date__gt=tour.start_date,
            ).values_list("guide_id", flat=True)

            # Exclude Guides whose user is in conflicting_user_ids
            qs = qs.exclude(user__id__in=conflicting_user_ids)

        return qs


# -------------------------
# Tour viewset
# -------------------------
# class TourViewSet(viewsets.ModelViewSet):
#     """
#     - Admins → Full CRUD on all tours
#     - Organizers → Full CRUD on their tours
#     - Tourists → Read-only
#     """
#     authentication_classes = [JWTAuthentication]
#     serializer_class = TourSerializer
#     permission_classes = [IsAdminOrOrganizerOwnerOrReadOnly]
#
#     def get_queryset(self):
#         user = self.request.user
#
#         # Tourists and unauthenticated users see all tours (read-only)
#         if not user.is_authenticated or user.role == 'tourist':
#             return Tour.objects.all().order_by('-start_date')
#
#         if user.role == 'organizer':
#             # Organizers see only their tours
#             return Tour.objects.filter(organizer=user).order_by('-start_date')
#
#         # Admin sees all tours
#         return Tour.objects.all().order_by('-start_date')
#
#     def perform_create(self, serializer):
#         # Only organizers or admins can create
#         if self.request.user.role not in ['organizer', 'admin']:
#             raise PermissionDenied("Only organizers or admins can create tours.")
#         serializer.save(organizer=self.request.user)
#
#     @method_decorator(vary_on_headers('Authorization'), name='list')
#     @method_decorator(cache_page(60 * 5))  # 5 min cache for list
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)
#
#     # Expose guide assignments for a tour via /tours/{pk}/guides/
#     @action(detail=True, methods=['get'], url_path='guides', permission_classes=[IsAuthenticated], authentication_classes = [JWTAuthentication])
#     def guides(self, request, pk=None):
#         tour = get_object_or_404(Tour, pk=pk)
#         # Only organizer of the tour or admin may list assignments (others should not)
#         if not (request.user.role == 'admin' or (request.user.role == 'organizer' and tour.organizer == request.user)):
#             return Response({'detail': 'Not authorized to view guide assignments for this tour.'}, status=status.HTTP_403_FORBIDDEN)
#
#         assignments = TourGuideAssignment.objects.filter(tour=tour)
#         serializer = TourGuideAssignmentSerializer(assignments, many=True)
#         return Response(serializer.data)
#
#     @action(detail=True, methods=['get'], url_path='participants', permission_classes=[IsAuthenticated])
#     def participants(self, request, pk=None):
#         tour = get_object_or_404(Tour, pk=pk)
#
#         # Permission check: only admin or organizer owner
#         if not (request.user.role == 'admin' or (request.user.role == 'organizer' and tour.organizer == request.user)):
#             return Response({'detail': 'Not authorized to view participants for this tour.'},
#                             status=status.HTTP_403_FORBIDDEN)
#
#         participants = TourParticipant.objects.filter(tour=tour)
#         serializer = ParticipantSerializer(participants, many=True)
#         return Response(serializer.data)
#
#     # @action(detail=True, methods=['get'], url_path='offers')
#     # def offers(self, request, pk=None):
#     #     tour = get_object_or_404(Tour, pk=pk)
#     #     offers = Offer.objects.filter(tour=tour)
#     #     serializer = OfferSerializer(offers, many=True)
#     #     return Response(serializer.data)
#     @action(detail=True, methods=['get', 'post'])
#     def offers(self, request, pk=None):
#         tour = self.get_object()
#
#         if request.method == 'GET':
#             serializer = OfferSerializer(tour.offers.all(), many=True)
#             return Response(serializer.data)
#
#         elif request.method == 'POST':
#             serializer = OfferSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             serializer.save(tour=tour)
#             return Response(serializer.data, status=201)

# -------------------------
# TourGuideAssignment viewset
# -------------------------
# -------------------------
# Pagination (server-side)
# -------------------------
class StandardResultsSetPagination(PageNumberPagination):
    # Sensible defaults; client can request up to 50
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 50


class SmallPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10


class TourViewSet(viewsets.ModelViewSet):
    """
    TourViewSet provides CRUD operations for Tour model with role-based access control:
    - Admins: full CRUD access to all tours
    - Organizers: full CRUD on tours they own
    - Tourists and unauthenticated users: read-only access to all tours
    """

    authentication_classes = [JWTAuthentication]
    serializer_class = TourSerializer
    permission_classes = [IsAdminOrOrganizerOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination

    # def get_queryset(self):
    #     """
    #     Return tours based on user role with optimized database queries.
    #
    #     Uses:
    #       - select_related: for single-valued relationships (ForeignKey) to reduce JOINs
    #       - prefetch_related: for reverse or many-to-many relations to reduce queries
    #
    #     Queryset behavior by role:
    #       - Tourists or anonymous users: all tours, read-only
    #       - Organizers: only tours they organize
    #       - Admin: all tours
    #
    #     Optimization details:
    #       - 'organizer' is ForeignKey, so select_related to join user once
    #       - 'guides' is ManyToManyField to Guide model, prefetch related guides
    #       - 'tour_participants' is reverse FK to TourParticipant, prefetch participants and also select related user in participants
    #       - 'offers' is reverse FK to Offer, prefetch offers
    #
    #     This drastically reduces the number of queries and improves performance.
    #     """
    #     user = self.request.user
    #
    #     # Base queryset with related fields optimized:
    #     # 'organizer' FK (single) → select_related
    #     # 'guides' M2M → prefetch_related
    #     # 'tour_participants' reverse FK → prefetch_related with select_related for user
    #     # 'offers' reverse FK → prefetch_related
    #     base_queryset = Tour.objects.select_related(
    #         'organizer'  # ForeignKey, single join for organizer user
    #     ).prefetch_related(
    #         'guides',  # ManyToMany guides
    #         # Prefetch participants with their related user to avoid N+1 when serializing user fields
    #         # 'tour_participants' is related_name for TourParticipant objects on Tour model
    #         'tour_participants__user',
    #         'offers',  # Offers related to this tour
    #     ).order_by('-start_date')
    #
    #     # Unauthenticated or tourist users see all tours read-only
    #     if not user.is_authenticated or user.role == 'tourist':
    #         return base_queryset
    #
    #     # Organizers see only their own tours
    #     if user.role == 'organizer':
    #         return base_queryset.filter(organizer=user)
    #
    #     # Admins see all tours
    #     return base_queryset
    # ---------- Queryset builder ----------
    def _base_queryset(self):
        """
        Shared base queryset with safe, targeted prefetches.
        NOTE: Avoid .only()/ .defer() unless you’ve verified serializer fields,
        because restricting columns can break serialization.
        """
        return (
            Tour.objects
            .select_related("organizer")
            .prefetch_related(
                # Guides: prefetch the related Guide objects (lightweight)
                "guides",
                # Participants with their user in one go
                Prefetch(
                    "tour_participants",
                    queryset=TourParticipant.objects.select_related("user")
                ),
                # Offers related to tour
                "offers",
            )
            .order_by("-start_date")
        )

    def get_queryset(self):
        user = self.request.user
        qs = self._base_queryset()

        # Role-based filtering
        if not user.is_authenticated or getattr(user, "role", "tourist") == "tourist":
            pass  # all tours
        elif user.role == "organizer":
            qs = qs.filter(organizer=user)
            if user.role == 'guide':
                return Tour.objects.filter(
                    guides__user=user,
                    tourguideassignment__status='accepted'
                ).distinct().order_by('-start_date')

        # ---- Server-side query filters ----
        category = self.request.query_params.get('category')
        location = self.request.query_params.get('start_location')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        search = self.request.query_params.get('search')

        if category:
            qs = qs.filter(category__iexact=category)
        if location:
            qs = qs.filter(start_location__iexact=location)
        if start_date:
            qs = qs.filter(start_date__gte=start_date)
        if end_date:
            qs = qs.filter(end_date__lte=end_date)
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(category__icontains=search) |
                Q(start_location__icontains=search) |
                Q(end_location__icontains=search)
            )

        return qs

    def perform_create(self, serializer):
        """
        Allow only admins or organizers to create tours.
        Automatically set the creator as organizer.
        """
        if self.request.user.role not in ['organizer', 'admin']:
            raise PermissionDenied("Only organizers or admins can create tours.")
        serializer.save(organizer=self.request.user)

    # ---------- Cached LIST for readonly audiences ----------
    # Vary on Authorization so authenticated and anonymous caches don't collide.
    @method_decorator(vary_on_headers("Authorization"))
    @method_decorator(cache_page(60 * 5))  # 5 minutes
    def list(self, request, *args, **kwargs):
        """
        Cached list endpoint. Because we paginate and vary on Authorization,
        admin/organizer/guide see their own fresh caches, while
        anonymous/tourist traffic benefits most from caching.
        """
        return super().list(request, *args, **kwargs)

    # @action(detail=True, methods=['get'], url_path='guides', permission_classes=[IsAuthenticated],
    #         authentication_classes=[JWTAuthentication])
    # def guides(self, request, pk=None):
    #     """
    #        List all guides **actually assigned to the tour** (accepted).
    #        Admins or the organizer can view all guides.
    #        """
    #     tour = get_object_or_404(Tour, pk=pk)
    #     if not (request.user.role == 'admin' or (request.user.role == 'organizer' and tour.organizer == request.user)):
    #         return Response({'detail': 'Not authorized to view guides for this tour.'},
    #                         status=status.HTTP_403_FORBIDDEN)
    #
    #     # Only show guides that were accepted
    #     accepted_assignments = TourGuideAssignment.objects.filter(tour=tour, status='accepted')
    #     serializer = self.get_serializer(accepted_assignments, many=True)
    #     return Response(serializer.data)
    @action(detail=True, methods=['get'], url_path='guides')
    def guides(self, request, pk=None):
        """
        List guides for a tour:
          - Only accepted guides for tourists
          - Organizer/Admin see all (accepted + pending)
        """
        tour = get_object_or_404(Tour, pk=pk)

        user = request.user
        if user.role not in ['admin', 'organizer', 'guide', 'tourist']:
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)

        if user.role in ['admin', 'organizer']:
            # Show all assignments
            assignments = TourGuideAssignment.objects.filter(tour=tour)
        elif user.role == 'guide':
            # Only self if accepted
            assignments = TourGuideAssignment.objects.filter(tour=tour, guide=user, status='accepted')
        else:
            # Only show accepted assignments
            assignments = TourGuideAssignment.objects.filter(tour=tour, status='accepted')

        # Ensure each assignment returns Guide object
        # Serializer already maps guide -> guide_profile
        serializer = TourGuideAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='participants', permission_classes=[IsAuthenticated])
    def participants(self, request, pk=None):
        """
        List participants of a specific tour.

        Permissions:
          - Only the tour organizer or admin can view participants.
        """
        tour = get_object_or_404(Tour, pk=pk)
        if not (request.user.role == 'admin' or (request.user.role == 'organizer' and tour.organizer == request.user)):
            return Response({'detail': 'Not authorized to view participants for this tour.'},
                            status=status.HTTP_403_FORBIDDEN)

        participants = TourParticipant.objects.filter(tour=tour)
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def offers(self, request, pk=None):
        """
        Get or create offers for a specific tour.

        GET: List all offers for the tour.
        POST: Create a new offer for the tour.
        """
        tour = self.get_object()

        if request.method == 'GET':
            serializer = OfferSerializer(tour.offers.all(), many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = OfferSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(tour=tour)
            return Response(serializer.data, status=201)


class TourGuideAssignmentViewSet(viewsets.GenericViewSet,
                                 mixins.ListModelMixin,
                                 mixins.DestroyModelMixin,
                                 mixins.UpdateModelMixin):
    """
    Endpoints:
    - POST   /tour-guide-assignments/assign-guide/  (organizer -> create assignments)
    - GET    /tour-guide-assignments/               (list by role)
    - POST   /tour-guide-assignments/{pk}/respond/ (guide respond)
    - DELETE /tour-guide-assignments/{pk}/cancel/  (organizer/admin cancel)
    - PATCH  /tour-guide-assignments/{pk}/         (admin override)
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = TourGuideAssignmentSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return TourGuideAssignment.objects.none()

        if user.role == 'admin':
            return TourGuideAssignment.objects.all().order_by('-assigned_at')

        if user.role == 'organizer':
            return TourGuideAssignment.objects.filter(tour__organizer=user).order_by('-assigned_at')

        if user.role == 'guide':
            return TourGuideAssignment.objects.filter(guide=user).order_by('-assigned_at')

        return TourGuideAssignment.objects.none()

    def get_permissions(self):
        # Map actions to permissions
        if self.action == 'assign_guide':
            permission_classes = [IsAuthenticated, IsOrganizerOrAdmin]
        elif self.action == 'respond':
            permission_classes = [IsAuthenticated, IsGuideSelf]
        elif self.action in ['destroy', 'cancel']:
            permission_classes = [IsAuthenticated, IsOrganizerOrAdmin]
        elif self.action == 'partial_update':
            permission_classes = [IsAdminUser]  # admin override
        else:
            permission_classes = [IsAuthenticated]
        return [perm() for perm in permission_classes]

    # -------------------------
    # Organizer assigns guides to a tour
    # -------------------------
    @action(detail=False, methods=['post'], url_path='assign-guide')
    def assign_guide(self, request):
        """
        Payload:
          {
            "tour_id": 5,
            "guide_ids": [10, 11]
          }
        """
        tour_id = request.data.get('tour_id')
        guide_ids = request.data.get('guide_ids', [])

        if not tour_id or not isinstance(guide_ids, list) or not guide_ids:
            return Response({"detail": "tour_id and guide_ids (non-empty list) are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        tour = get_object_or_404(Tour, id=tour_id)

        # Check permission
        user = request.user
        if not (user.role == 'admin' or (user.role == 'organizer' and tour.organizer == user)):
            return Response({'detail': 'Not authorized to assign guides to this tour.'},
                            status=status.HTTP_403_FORBIDDEN)

        created = []
        skipped = []
        try:
            with transaction.atomic():
                for guide_id in guide_ids:
                    # guide in your model is a User (limit_choices_to={'role': 'guide'})
                    guide_user = None
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    guide_user = User.objects.filter(id=guide_id, role='guide').first()

                    if not guide_user:
                        skipped.append({"guide_id": guide_id, "reason": "guide not found or not role 'guide'"})
                        continue

                    # No duplicates: unique_together on (tour, guide)
                    exists = TourGuideAssignment.objects.filter(tour=tour, guide=guide_user,
                                                                status__in=['pending', 'accepted']).exists()
                    if exists:
                        skipped.append({"guide_id": guide_id, "reason": "already assigned or pending"})
                        continue

                    assignment = TourGuideAssignment.objects.create(tour=tour, guide=guide_user, status='pending')
                    created.append(assignment)
        except IntegrityError:
            return Response({"detail": "Database error while creating assignments."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(created, many=True)
        response_data = {"created": serializer.data, "skipped": skipped}
        return Response(response_data, status=status.HTTP_201_CREATED)

    # -------------------------
    # Guide responds to their assignment
    # -------------------------
    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        assignment = get_object_or_404(TourGuideAssignment, pk=pk)
        # permission checked by get_permissions -> IsGuideSelf

        new_status = request.data.get('status')
        if new_status not in ['accepted', 'declined']:
            return Response(
                {'detail': 'Invalid status. Acceptable: accepted, declined.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update responded_at timestamp
        assignment.status = new_status
        assignment.responded_at = timezone.now()
        assignment.save()

        # If accepted → add guide to Tour.guides (Guide model, not User)
        if new_status == 'accepted':
            try:
                guide_profile = assignment.guide.guide  # because User → OneToOne → Guide
                assignment.tour.guides.add(guide_profile)
            except Guide.DoesNotExist:
                return Response(
                    {'detail': 'Guide profile not found for this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # -------------------------
    # Cancel pending assignment (organizer/admin)
    # -------------------------
    @action(detail=True, methods=['delete'], url_path='cancel')
    def cancel(self, request, pk=None):
        assignment = get_object_or_404(TourGuideAssignment, pk=pk)

        if not (request.user.role == 'admin' or (
                request.user.role == 'organizer' and assignment.tour.organizer == request.user)):
            return Response({'detail': 'Not authorized to cancel this assignment.'}, status=status.HTTP_403_FORBIDDEN)

        if assignment.status != 'pending':
            return Response({'detail': 'Only pending assignments can be canceled.'}, status=status.HTTP_400_BAD_REQUEST)

        assignment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # partial_update -> admin override handled by mixin UpdateModelMixin (permission = IsAdminUser)
    # destroy -> default destroy is available via mixin.DestroyModelMixin (permission checks above)


# -------------------------
# Offers and Participants (you already had these; keep but with error handling)
# -------------------------
class OfferViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated, IsAdminOrOrganizerOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Offer.objects.all()

        # Organizers only see their own offers
        if user.role == "organizer":
            queryset = queryset.filter(tour__organizer=user)

        # Tour-specific filter via query param
        tour_id = self.request.query_params.get("tour")
        if tour_id:
            queryset = queryset.filter(tour_id=tour_id)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        tour = serializer.validated_data.get("tour", None)

        if tour:
            if user.role == "organizer" and tour.organizer != user:
                raise PermissionDenied("You are not the organizer of this tour.")
            serializer.save(tour=tour)  # ✅ no 'organizer' here
        else:
            if user.role != "organizer":
                raise PermissionDenied("Only organizers can create global offers.")

            tours = Tour.objects.filter(organizer=user)
            for t in tours:
                serializer.save(tour=t)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """
        Create the same offer for all tours owned by the organizer
        """
        user = request.user
        if user.role != "organizer":
            return Response({"detail": "Only organizers can bulk create offers."},
                            status=status.HTTP_403_FORBIDDEN)

        data = request.data
        tours = Tour.objects.filter(organizer=user)

        offers = []
        for tour in tours:
            serializer = OfferSerializer(data={**data, "tour": tour.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            offers.append(serializer.data)

        return Response(offers, status=status.HTTP_201_CREATED)


class TourParticipantViewSet(viewsets.ModelViewSet):
    queryset = TourParticipant.objects.all()
    serializer_class = ParticipantSerializer
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return TourParticipant.objects.none()

        if user.role == 'admin':
            return TourParticipant.objects.all()
        elif user.role == 'organizer':
            return TourParticipant.objects.filter(tour__organizer=user)
        else:
            return TourParticipant.objects.filter(user=user)

    # def perform_create(self, serializer):
    #     user = self.request.user
    #     if not user.is_authenticated or user.role != 'tourist':
    #         raise PermissionDenied("Only tourists can join tours.")
    #     # Initial status set to pending
    #     serializer.save(user=user, status='pending')
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_authenticated or user.role != 'tourist':
            raise PermissionDenied("Only tourists can join tours.")

        tour_id = self.request.data.get("tour")  # Make sure the tour ID comes in the request
        tour = get_object_or_404(Tour, pk=tour_id)

        # Check if the user already joined
        if TourParticipant.objects.filter(user=user, tour=tour).exists():
            raise PermissionDenied("You have already joined this tour.")

        serializer.save(user=user, tour=tour, status='pending')

    @action(detail=True, methods=['patch'], url_path='approve')
    def approve_participant(self, request, pk=None):
        participant = self.get_object()
        # Only organizer of the tour or admin
        if request.user.role not in ['admin', 'organizer'] or (
                request.user.role == 'organizer' and participant.tour.organizer != request.user):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        participant.status = 'approved'
        participant.save()
        return Response({"detail": "Participant approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='reject')
    def reject_participant(self, request, pk=None):
        participant = self.get_object()
        if request.user.role not in ['admin', 'organizer'] or (
                request.user.role == 'organizer' and participant.tour.organizer != request.user):
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        participant.status = 'rejected'
        participant.save()
        return Response({"detail": "Participant rejected."}, status=status.HTTP_200_OK)


# class BookingViewSet(viewsets.ModelViewSet):
#     queryset = Booking.objects.all()
#     serializer_class = BookingSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         qs = Booking.objects.all()
#         user = self.request.user
#
#         if user.role == "admin":
#             qs = qs
#         elif user.role == "organizer":
#             qs = qs.filter(participant__tour__organizer=user)
#         else:
#             qs = qs.filter(participant__user=user)
#
#         participant_id = self.request.query_params.get("participant")
#         if participant_id:
#             qs = qs.filter(participant__id=participant_id)
#
#         return qs
#
#     def perform_create(self, serializer):
#         user = self.request.user
#         if user.role != "tourist":
#             return Response({"detail": "Only tourists can create bookings."}, status=403)
#
#         participant_id = self.request.data.get("participant")
#         participant = get_object_or_404(TourParticipant, id=participant_id)
#
#         if participant.user != user:
#             return Response({"detail": "You can only create bookings for yourself."}, status=403)
#
#         # Default: new payment is pending
#         serializer.save(participant=participant, payment_status="pending")
#
#     @action(detail=True, methods=["patch"], url_path="pay")
#     def pay(self, request, pk=None):
#         """
#         Tourist marks a payment (partial or full).
#         payload: { "amount": 50.00 }
#         """
#         booking = self.get_object()
#         user = request.user
#
#         if user.role != "tourist" or booking.participant.user != user:
#             return Response({"detail": "Permission denied."}, status=403)
#
#         amount = request.data.get("amount")
#         if not amount:
#             return Response({"detail": "Amount required."}, status=400)
#
#         amount = float(amount)
#         booking.amount_paid = (booking.amount_paid or 0) + amount
#
#         # Update payment status
#         if booking.amount_paid < booking.amount:
#             booking.payment_status = "partial"
#         else:
#             booking.payment_status = "paid"
#             booking.paid_at = timezone.now()
#
#         booking.save()
#         return Response(BookingSerializer(booking).data)
#
#     @action(detail=True, methods=["patch"], url_path="verify")
#     def verify_payment(self, request, pk=None):
#         """
#         Organizer/admin verifies manual/cash payment.
#         """
#         booking = self.get_object()
#         user = request.user
#
#         if user.role not in ["admin", "organizer"]:
#             return Response({"detail": "Permission denied."}, status=403)
#         if user.role == "organizer" and booking.participant.tour.organizer != user:
#             return Response({"detail": "Permission denied."}, status=403)
#
#         if booking.payment_status in ["pending", "partial"]:
#             booking.payment_status = "paid"
#             booking.amount_paid = booking.amount
#             booking.paid_at = timezone.now()
#             booking.save()
#             return Response({"detail": "Payment verified and marked as paid."})
#         else:
#             return Response({"detail": "Payment already completed or failed."}, status=400)


class TouristToursView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    pagination_class = SmallPagination

    def get_queryset_for_status(self, tour_ids, now_date):
        """
        Helper to return Tour queryset with safe prefetches
        """
        return (
            Tour.objects.filter(id__in=tour_ids)
            .select_related("organizer")
            .prefetch_related(
                "offers",
                "tour_participants__user",
                "guide_assignments__guide__guide",
            )
        )

    def paginate_queryset(self, queryset, request):
        paginator = self.pagination_class()
        return paginator.paginate_queryset(queryset, request), paginator

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=401,
            )

        now_date = now()

        try:
            # Fetch all participations for user
            user_participations = (
                TourParticipant.objects.filter(user=user)
                .select_related("tour")
                .only("id", "status", "tour_id", "tour__organizer_id")
            )

            participations_by_status = {}
            joined_tour_ids = []
            for part in user_participations:
                participations_by_status.setdefault(part.status, []).append(part.tour_id)
                joined_tour_ids.append(part.tour_id)

            # ---------------------
            # Available tours (not joined, future)
            # ---------------------
            available_qs = (
                Tour.objects.exclude(id__in=joined_tour_ids)
                .filter(start_date__gte=now_date)
                .select_related("organizer")
                .prefetch_related(
                    "offers",
                    "tour_participants__user",
                    "guide_assignments__guide__guide",
                )
            )
            available, paginator_avail = self.paginate_queryset(available_qs, request)

            # ---------------------
            # Pending tours
            # ---------------------
            pending_ids = participations_by_status.get("pending", [])
            pending_qs = self.get_queryset_for_status(pending_ids, now_date)
            pending, paginator_pending = self.paginate_queryset(pending_qs, request)

            # ---------------------
            # Active tours
            # ---------------------
            active_ids = participations_by_status.get("approved", [])
            active_qs = (
                self.get_queryset_for_status(active_ids, now_date)
                .filter(end_date__gte=now_date)
            )
            active, paginator_active = self.paginate_queryset(active_qs, request)

            # ---------------------
            # Past tours
            # ---------------------
            past_ids = active_ids + participations_by_status.get("completed", [])
            past_qs = (
                self.get_queryset_for_status(past_ids, now_date)
                .filter(end_date__lt=now_date)
            )
            past, paginator_past = self.paginate_queryset(past_qs, request)

            context = {"user": user}
            data = {
                "available_tours": TourSerializer(available, many=True, context=context).data,
                "pending_tours": TourSerializer(pending, many=True, context=context).data,
                "active_tours": TourSerializer(active, many=True, context=context).data,
                "past_tours": TourSerializer(past, many=True, context=context).data,
            }

            return Response(data, status=200)

        except Exception as e:
            import traceback
            print("❌ TouristToursView crashed:", traceback.format_exc())
            return Response(
                {"error": "Unexpected error: " + str(e)},
                status=500,
            )


class DashboardStatsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOrganizerOrAdmin]

    def get(self, request):
        user = request.user
        cache_key = f'dashboard_stats_{user.role}_{user.id}'
        stats = cache.get(cache_key)

        if not stats:
            # Admin stats
            if user.role == 'admin':
                total_users = User.objects.count()
                active_users = User.objects.filter(
                    last_login__gte=timezone.now() - timezone.timedelta(days=30)
                ).count()
                sessions = Session.objects.filter(expire_date__gte=timezone.now())
                session_user_ids = [
                    s.get_decoded().get('_auth_user_id')
                    for s in sessions
                    if s.get_decoded().get('_auth_user_id')
                ]
                currently_logged_in = len(set(session_user_ids))
                total_tours = Tour.objects.count()
                approved_bookings = TourParticipant.objects.filter(status__iexact="approved").count()
                pending_requests = TourParticipant.objects.filter(status__iexact="pending").count()
                total_guides = Guide.objects.count()
                user_tours = Tour.objects.all()
            # Organizer stats
            elif user.role == 'organizer':
                total_users = active_users = currently_logged_in = total_guides = None
                user_tours = Tour.objects.filter(organizer=user)
                total_tours = user_tours.count()
                approved_bookings = TourParticipant.objects.filter(
                    tour__organizer=user, status__iexact="approved"
                ).count()
                pending_requests = TourParticipant.objects.filter(
                    tour__organizer=user, status__iexact="pending"
                ).count()
            else:
                return Response({"detail": "Forbidden"}, status=403)

            stats = {
                "total_users": total_users,
                "active_users": active_users,
                "currently_logged_in": currently_logged_in,
                "total_tours": total_tours,
                "approved_bookings": approved_bookings,
                "pending_requests": pending_requests,
                "total_guides": total_guides,
            }
            cache.set(cache_key, stats, 60 * 5)  # cache per role+user for 5 min

        # Recent activity
        recent_users = []
        if user.role == 'admin':
            recent_users = list(
                User.objects.order_by('-id').values('id', 'username', 'last_login')[:5]
            )

        recent_tours = list(
            Tour.objects.filter(organizer=user).order_by('-start_date').values('id', 'title', 'start_date')[:5]
            if user.role == 'organizer'
            else Tour.objects.order_by('-start_date').values('id', 'title', 'start_date')[:5]
        )

        return Response({
            "stats": stats,
            "recent_users": recent_users,
            "recent_tours": recent_tours
        })
