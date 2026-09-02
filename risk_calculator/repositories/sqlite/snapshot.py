import sqlite3
from datetime import datetime
from pathlib import Path

from risk_calculator.domain.snapshot import PortfolioSnapshot, PositionSnapshot
from risk_calculator.repositories.protocols import PortfolioSnapshotRepository


class SQLitePortfolioSnapshotRepository(PortfolioSnapshotRepository):
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def get(self, snapshot_id: str) -> PortfolioSnapshot | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            # first fetch snapshot header
            header = conn.execute(
                """
                SELECT id, timestamp, total_value, total_margin, source, label
                FROM portfolio_snapshots
                WHERE id = ?
                """,
                (snapshot_id,),
            ).fetchone()

            if not header:
                return None

            # fetch position snapshots for this portfolio snapshot
            position_rows = conn.execute(
                """
                SELECT
                    symbol,
                    quantity,
                    price,
                    instrument_type,
                    margin_rate,
                    value,
                    margin
                FROM position_snapshots
                WHERE snapshot_id = ?
                ORDER BY symbol
                """,
                (snapshot_id,),
            ).fetchall()

            position_snapshots = [
                PositionSnapshot(
                    symbol=row_data["symbol"],
                    quantity=row_data["quantity"],
                    price=row_data["price"],
                    instrument_type=row_data["instrument_type"],
                    margin_rate=row_data["margin_rate"],
                    value=row_data["value"],
                    margin=row_data["margin"],
                )
                for row_data in position_rows
            ]

            snapshot = PortfolioSnapshot(
                id=snapshot_id,
                timestamp=datetime.fromisoformat(header["timestamp"]),
                total_value=header["total_value"],
                total_margin=header["total_margin"],
                source=header["source"],
                label=header["label"],
                positions=position_snapshots,
            )
            return snapshot

    def get_all(self) -> list[PortfolioSnapshot]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, timestamp, total_value, total_margin, source, label
                FROM portfolio_snapshots
                ORDER BY timestamp DESC
                """
            ).fetchall()

            snapshots = [
                PortfolioSnapshot(
                    id=row_data["id"],
                    timestamp=datetime.fromisoformat(row_data["timestamp"]),
                    total_value=row_data["total_value"],
                    total_margin=row_data["total_margin"],
                    source=row_data["source"],
                    label=row_data["label"],
                    positions=[],
                )
                for row_data in rows
            ]
            return snapshots

    def save(self, snapshot: PortfolioSnapshot) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO portfolio_snapshots (id, timestamp, total_value, total_margin, source, label)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.id,
                    snapshot.timestamp.isoformat(),
                    snapshot.total_value,
                    snapshot.total_margin,
                    snapshot.source,
                    snapshot.label,
                ),
            )
            for position_snapshot in snapshot.positions:
                conn.execute(
                    """
                    INSERT INTO position_snapshots (snapshot_id, symbol, quantity, price, instrument_type, margin_rate, value, margin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot.id,
                        position_snapshot.symbol,
                        position_snapshot.quantity,
                        position_snapshot.price,
                        position_snapshot.instrument_type,
                        position_snapshot.margin_rate,
                        position_snapshot.value,
                        position_snapshot.margin,
                    ),
                )

    def update(self, snapshot_id: str, source: str | None = None, label: str | None = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                UPDATE portfolio_snapshots
                SET source = COALESCE(?, source),
                    label = COALESCE(?, label)
                WHERE id = ?
                """,
                (source, label, snapshot_id),
            )
            return cursor.rowcount
