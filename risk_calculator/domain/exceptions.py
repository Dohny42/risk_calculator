class DomainError(Exception):
    """Base class for all domain errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class InvalidInstrumentError(DomainError): ...


class InvalidPositionError(DomainError): ...


class UnknownInstrumentError(DomainError):
    def __init__(self, symbol: str):
        super().__init__(f"Instrument with symbol '{symbol}' not found.")


class UnknownPositionError(DomainError):
    def __init__(self, symbol: str):
        super().__init__(f"Position for symbol '{symbol}' not found.")


class UnknownSymbolsError(DomainError):
    def __init__(self, symbols: list[str]):
        super().__init__(f"Unknown symbols in price changes: {symbols}")


class UnknownStressScenarioError(DomainError):
    def __init__(self, name: str):
        super().__init__(f"Stress scenario with name '{name}' not found.")


class InvalidStressScenarioError(DomainError): ...


class StressScenarioAlreadyExistsError(DomainError):
    def __init__(self, name: str):
        super().__init__(f"Stress scenario with name '{name}' already exists.")


class UnknownPortfolioSnapshotError(DomainError):
    def __init__(self, snapshot_id: str):
        super().__init__(f"Portfolio snapshot with ID '{snapshot_id}' not found.")
