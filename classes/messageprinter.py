class TermColor:
    BOLD = '\033[1m'
    BOLD_RED = '\033[1;31m'
    BOLD_GREEN = '\033[1;32m'
    BOLD_YELLOW = '\033[1;33m'
    BOLD_BLUE = '\033[1;34m'
    RESET = '\033[0m'


class MessagePrinter:
    @staticmethod
    def print_plain(x):
        print(TermColor.BOLD + '    ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)

    @staticmethod
    def print_msg(x):
        print(TermColor.BOLD_GREEN + '==> ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)

    @staticmethod
    def print_msg2(x):
        print(TermColor.BOLD_BLUE + ' -> ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)

    @staticmethod
    def print_warning(x):
        print(TermColor.BOLD_YELLOW + '==> ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)

    @staticmethod
    def print_error(x):
        print(TermColor.BOLD_RED + '==> ERROR: ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)
