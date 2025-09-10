from lectes.errors import LectesError


class EngineError(LectesError):
    """
    Base class for all errors occuring in the regex engine.
    """


class RegexPatternError(EngineError):
    """
    The regular expression is invalid or not recognized.
    """
