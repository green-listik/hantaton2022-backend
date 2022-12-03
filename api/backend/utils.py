from sqlalchemy.ext.asyncio import AsyncSession

from api.backend.schemas import Dots
from crud import get_event_by_id
from schemas import Dots


async def get_dots(db: AsyncSession, event_id: int) -> Dots | None:
    event = await get_event_by_id(db, event_id)
    if event is None:
        return None
    planned = []
    actual = []
    planned_day = 0
    actual_day = 0
    for operation in event.operations:
        planned_depth = operation.parameters.get('planned_depth')
        actual_depth = operation.parameters.get('actual_depth')
        planned_day = operation.parameters.get('planned_time') / 24 + planned_day
        actual_day = operation.parameters.get('actual_time') / 24 + actual_day
        planned.append((planned_day, planned_depth))
        actual.append((actual_day, actual_depth))
    return Dots(planned=planned, actual=actual)
