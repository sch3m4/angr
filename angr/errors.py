class AngrError(Exception):
    pass

class AngrMemoryError(AngrError):
    pass

class AngrTranslationError(AngrError):
    pass

class AngrExitError(AngrError):
    pass

class AngrPathError(AngrError):
    pass