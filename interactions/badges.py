"""Admin sidebar badges (referenced from UNFOLD["SIDEBAR"] in settings).

Unfold always renders a badge given as a callback path, so an empty count would
show up as "None". A static badge object is rendered only when it is truthy, so
this one evaluates to False when there is nothing to review and hides itself.
Models are imported lazily because settings import this module.
"""


class OpenReportsBadge:
    @staticmethod
    def _count() -> int:
        from .models import Report

        return Report.objects.filter(status=Report.OPEN).count()

    def __bool__(self) -> bool:
        return self._count() > 0

    def __str__(self) -> str:
        return str(self._count())
