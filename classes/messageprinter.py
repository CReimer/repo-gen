from classes.termcolor import TermColor


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
        print(TermColor.BOLD_RED + '==> ' + TermColor.RESET + TermColor.BOLD + x + TermColor.RESET)
