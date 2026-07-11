class MacroError(Exception):
    pass


class MacroNotFoundError(MacroError):
    pass


class CorruptedMacroError(MacroError):
    pass


class InvalidMacroNameError(MacroError):
    pass


class EditingNotAllowedError(MacroError):
    pass
