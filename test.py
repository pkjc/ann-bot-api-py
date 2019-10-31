uq_set = set(["sentence", "This", "hey"])
rule_set = set(["sentence", "This", "h"])
overlap = uq_set.intersection(rule_set)

print(len(overlap))