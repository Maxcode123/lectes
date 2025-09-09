from lectes import Rule, Configuration, Regex, Scanner


def handle(unmatched):
    print(f"custom handler: {unmatched}")


rule1 = Rule("FOR", Regex("for"))
rule2 = Rule("WHITESPACE", Regex("( )"))
rule3 = Rule("LET", Regex("let"))

config = Configuration([rule1, rule2, rule3])

scanner = Scanner(config)
scanner.set_unmatched_handler(handle)

program = "for asada let in let"

for token in scanner.scan(program):
    print(token)
