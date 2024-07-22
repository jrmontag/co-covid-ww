from enum import Enum


class CdpheObservation(Enum):
    # CDPHE-defined fields
    OBJECTID: str = "OBJECTID"
    DATE = "Date"
    UTILITY = "Utility"
    COPIES_LP1 = "SARS-CoV-2 copies/L (Lab Phase 1)"
    COPIES_LP2 = "SARS-CoV-2 copies/L (Lab Phase 2)"
    CASES = "Number of New COVID19 Cases by Onset Date (3-Day Average)"
    PHASE = "Lab Phase"
