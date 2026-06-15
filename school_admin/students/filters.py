"""
Student search & filter logic.

WHY A SEPARATE FILTERS MODULE?
───────────────────────────────
Search/filter logic can get complex. Keeping it in a dedicated module:
  - Keeps views clean (views call filters, not implement them)
  - Makes filters testable independently
  - Easy to add new filters without touching views

HOW IT WORKS:
  filter_students() takes a queryset and a dict of filter params
  (from request.GET), applies each filter if the param is present,
  and returns the filtered queryset.

  Django's ORM chains filters: each .filter() adds an AND condition.
  Q objects let us do OR conditions (e.g., search name OR student number).
"""

from django.db.models import Q


def filter_students(queryset, params):
    """
    Apply search and filters to a student queryset.

    Args:
        queryset: StudentProfile.objects.all() (or pre-filtered)
        params: request.GET dict with filter keys

    Returns:
        Filtered queryset
    """
    # ── Free-text search (searches across multiple fields) ──
    search = params.get("q", "").strip()
    if search:
        queryset = queryset.filter(
            Q(student_name__icontains=search)
            | Q(student_number__icontains=search)
            | Q(email__icontains=search)
            | Q(parent_info__father_name__icontains=search)
            | Q(parent_info__mother_name__icontains=search)
            | Q(parent_info__father_phone__icontains=search)
            | Q(parent_info__mother_phone__icontains=search)
            | Q(catechism_info__catechism_teacher_name__icontains=search)
        )

    # ── Dropdown filters (exact match) ──────────────────────
    school_class = params.get("school_class")
    if school_class:
        queryset = queryset.filter(school_class_id=school_class)

    division = params.get("division")
    if division:
        queryset = queryset.filter(division_id=division)

    status = params.get("status")
    if status:
        queryset = queryset.filter(status=status)

    gender = params.get("gender")
    if gender:
        queryset = queryset.filter(gender=gender)

    provision = params.get("provision")
    if provision:
        queryset = queryset.filter(catechism_info__provision_id=provision)

    unit = params.get("unit")
    if unit:
        queryset = queryset.filter(catechism_info__unit_id=unit)

    attended_catechism = params.get("attended_catechism")
    if attended_catechism:
        queryset = queryset.filter(attended_catechism=(attended_catechism == "yes"))

    return queryset.distinct()
