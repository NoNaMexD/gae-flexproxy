class QueryEngine:
    def _match(self, item, matcher, op='auto'):
        if (op == 'auto' and len(matcher) >= 3 and matcher[0] == '/' and matcher[-1] == '/'):
            if (re.match(matcher[1:-1], item)):
                return True
            else:
                return False
        elif (op == 'regex'):
            if (re.match(matcher, item)):
                return True
            else:
                return False
        elif (op == 'exact'):
            if (matcher.lower() == item.lower()):
                return True
            else:
                return False
        else:
            raise ValueError, "unknown match type: " + op
