from risk_calculator.domain.exceptions import UnknownPortfolioSnapshotError
from risk_calculator.domain.snapshot import PortfolioSnapshot, create_portfolio_snapshot
from risk_calculator.repositories.protocols import PortfolioRepository, PortfolioSnapshotRepository


class PortfolioSnapshotService:
    def __init__(
        self,
        portfolio_repository: PortfolioRepository,
        snapshot_repository: PortfolioSnapshotRepository,
    ):
        self.portfolio_repository = portfolio_repository
        self.snapshot_repository = snapshot_repository

    def create_snapshot(self, source: str = "live", label: str | None = None) -> PortfolioSnapshot:
        portfolio = self.portfolio_repository.get()
        snapshot = create_portfolio_snapshot(portfolio, source, label)
        self.snapshot_repository.save(snapshot)
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> PortfolioSnapshot:
        snapshot = self.snapshot_repository.get(snapshot_id)
        if snapshot is None:
            raise UnknownPortfolioSnapshotError(snapshot_id)
        return snapshot

    def list_snapshots(self) -> list[PortfolioSnapshot]:
        return self.snapshot_repository.get_all()

    def update(
        self, snapshot_id: str, source: str | None = None, label: str | None = None
    ) -> PortfolioSnapshot:
        updated_rows_count = self.snapshot_repository.update(snapshot_id, source, label)
        if updated_rows_count == 0:
            raise UnknownPortfolioSnapshotError(snapshot_id)
        return self.get_snapshot(snapshot_id)
