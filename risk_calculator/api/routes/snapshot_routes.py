from fastapi import APIRouter, Depends

from risk_calculator.api.dependencies import get_snapshot_service
from risk_calculator.api.schemas import (
    PortfolioSnapshotResponse,
    PositionResponse,
)
from risk_calculator.domain.snapshot import PortfolioSnapshot
from risk_calculator.services.snapshot_service import PortfolioSnapshotService

router = APIRouter()


def to_portfolio_snapshot_response(snapshot: PortfolioSnapshot) -> PortfolioSnapshotResponse:
    return PortfolioSnapshotResponse(
        timestamp=snapshot.timestamp,
        positions=[
            PositionResponse(
                symbol=p.symbol,
                quantity=p.quantity,
                price=p.price,
                instrument_type=p.instrument_type,
                value=p.value,
                margin=p.margin,
            )
            for p in snapshot.positions
        ],
        total_value=snapshot.total_value,
        total_margin=snapshot.total_margin,
        source=snapshot.source,
        label=snapshot.label,
    )


@router.get("/snapshots", response_model=list[PortfolioSnapshotResponse])
def list_snapshots(
    snapshot_service: PortfolioSnapshotService = Depends(get_snapshot_service),
) -> list[PortfolioSnapshotResponse]:
    snapshots = snapshot_service.list_snapshots()
    return [to_portfolio_snapshot_response(snapshot) for snapshot in snapshots]


@router.get("/snapshots/{snapshot_id}", response_model=PortfolioSnapshotResponse)
def get_snapshot(
    snapshot_id: str,
    snapshot_service: PortfolioSnapshotService = Depends(get_snapshot_service),
) -> PortfolioSnapshotResponse:
    snapshot = snapshot_service.get_snapshot(snapshot_id)
    return to_portfolio_snapshot_response(snapshot)


@router.post("/snapshots", response_model=PortfolioSnapshotResponse)
def create_snapshot(
    snapshot_service: PortfolioSnapshotService = Depends(get_snapshot_service),
    source: str = "live",
    label: str | None = None,
) -> PortfolioSnapshotResponse:
    snapshot = snapshot_service.create_snapshot(source, label)
    return to_portfolio_snapshot_response(snapshot)
