class Couleurs:
    CSI = "\x1b["
    RESET = CSI + "0m"
    BLEU = CSI + "94m"
    VERT = CSI + "92m"
    JAUNE = CSI + "93m"
    ROUGE = CSI + "91m"
    CYAN = CSI + "96m"

    def print_bleu(self, msg): print(f"{self.BLEU}{msg}{self.RESET}")
    def print_vert(self, msg): print(f"{self.VERT}{msg}{self.RESET}")
    def print_jaune(self, msg): print(f"{self.JAUNE}{msg}{self.RESET}")
    def print_rouge(self, msg): print(f"{self.ROUGE}{msg}{self.RESET}")
    def print_cyan(self, msg): print(f"{self.CYAN}{msg}{self.RESET}")

couleur = Couleurs()