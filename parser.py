import sys
import re

__author__ = 'Jerry'


TRUE = ":^)"
FALSE = ":^{"
truefalse = [TRUE, FALSE]


def is_literal(token):
    return (token.startswith('\'') and token.endswith('\'')) or (token.startswith('\"') and token.endswith('\"'))


def is_float(token):
    try:
        float(token)
        return True
    except ValueError:
        return False


def do_operation(operator, operand1, operand2):
    if operator == '+':
        return operand1 + operand2
    elif operator == '-':
        return operand1 - operand2
    elif operator == '*':
        return operand1 * operand2
    elif operator == '/':
        return operand1 / operand2
    elif operator == '%':
        return int(operand1) % int(operand2)
    else:
        raise ValueError


class Parser:

    variables = {}

    def __init__(self):
        pass

    def parse_boolean(self, tokens):
        keywords = ["is", "isn\'t", "<", ">", "<=", ">=", "and", "or", "not"]
        new_tokens = []

        for token in tokens:
            if token in keywords:
                new_tokens.append(token)
            else:
                if is_literal(token):
                    new_tokens.append(token[1:-1])
                elif token.isdigit():
                    new_tokens.append(int(token))
                elif is_float(token):
                    new_tokens.append(float(token))
                elif token in self.variables:
                    new_tokens.append(self.variables[token])
                else:
                    print "wtf can't read", token
                    return "invalid"

        for i in range(0, len(new_tokens)):
            token = new_tokens[i]
            # print token

            try:
                prev_token = new_tokens[i - 1]
                next_token = new_tokens[i + 1]
            except IndexError:
                print "wtf can't read this"
                return "invalid"

            if token == "is":
                return TRUE if prev_token == next_token else FALSE
            elif token == "isn\'t":
                return TRUE if prev_token != next_token else FALSE
            elif token == "<":
                return TRUE if prev_token < next_token else FALSE
            elif token == ">":
                return TRUE if prev_token > next_token else FALSE
            elif token == "<=":
                return TRUE if prev_token <= next_token else FALSE
            elif token == ">=":
                return TRUE if prev_token >= next_token else FALSE

    def parse_math(self, src_tokens):
        keywords = ['(', ')', '*', '/', '+', '-', '%']
        operators = ['*', '/', '+', '-', '%']
        tokens = src_tokens

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.isdigit():
                tokens[i] = int(token)
            elif is_float(token):
                tokens[i] = float(token)
            elif token in self.variables:
                tokens[i] = self.variables[token]
            elif token in keywords:
                tokens[i] = token
            elif any(c in token for c in keywords):
                split_tokens = [t for t in re.split("(\(|\)|\*|/|\+|\-|%)", token) if len(t) > 0]
                tokens.pop(i)
                tokens[i:i] = split_tokens
                i -= 1
            else:
                print "wtf can't read", token
                return None
            i += 1

        try:
            operator, operand = [], []
            i = 0
            while i < len(tokens):
                t = tokens[i]
                # print t, operand, operator
                if t in operators:
                    operator.append(t)
                elif t == ')':
                    if len(operand) > 1:
                        op2 = operand.pop()
                        op1 = operand.pop()
                        operand.append(do_operation(operator.pop(), op1, op2))
                elif is_float(t):
                    if tokens[i - 1] == '(':
                        operand.append(float(tokens[i]))
                    else:
                        if len(operand) == 0:
                            operand.append(float(t))
                        else:
                            op = operand.pop()
                            operand.append(do_operation(operator.pop(), op, float(t)))
                i += 1
            return operand.pop()
        except ValueError:
            print "wtf can't math this"
            return None

    # def parse_expression(self, tokens):
    #     boolean_result = self.parse_boolean(tokens)
    #     if boolean_result in truefalse:
    #         return
    #     else:
    #         return self.parse_math(tokens)

    def parse(self, lines):

        call_stack = []
        condition_execution_stack = []
        condition_scope_stack = []

        line_count = 0

        while line_count < len(lines):
            tokens = lines[line_count].split()
            # print tokens
            tokens_len = len(tokens)

            # Skip blank lines and commented out lines
            if tokens_len == 0:
                continue

            # Skip line if this is not the right conditional branch UNLESS for conditional statements
            if (condition_scope_stack != condition_execution_stack) \
                    and not ((tokens[0] == "implying")
                            or ((tokens_len == 2) and (tokens[0] == "or") and (tokens[1] == "not"))
                            or ((tokens_len == 2) and (tokens[0] == "done") and (tokens[1] == "implying"))):
                line_count += 1
                continue

            if (tokens[0] == "mfw") and (tokens_len > 1):
                for token in tokens[1:]:
                    if is_literal(token):
                        print token[1:-1],
                    elif token.isdigit() or is_float(token):
                        print token,
                    elif token in self.variables:
                        print self.variables[token],
                print

            elif tokens[0] == "be":
                if tokens_len > 2:
                    if is_literal(tokens[2]):
                        self.variables[tokens[1]] = tokens[2][1:-1]
                    elif tokens[2].isdigit() and tokens_len == 3:
                        self.variables[tokens[1]] = int(tokens[2])
                    elif is_float(tokens[2]) and tokens_len == 3:
                        self.variables[tokens[1]] = float(tokens[2])
                    elif tokens[2] in self.variables and tokens_len == 3:
                        self.variables[tokens[1]] = self.variables[tokens[2]]
                    else:
                        parse_result = self.parse_math(tokens[2:])
                        if parse_result is None:
                            print "wtf can't be this"
                            return
                        else:
                            self.variables[tokens[1]] = parse_result

            elif tokens[0] == "implying":
                condition_scope_stack.append(TRUE)

                # Single boolean argument
                if tokens_len == 2:
                    if is_literal(tokens[1]):
                        if tokens[1][1:-1] in truefalse:
                            condition_execution_stack.append(tokens[1][1:-1])
                    elif (tokens[1] in self.variables) and (self.variables[tokens[1]] in truefalse):
                        condition_execution_stack.append(self.variables[tokens[1]])

                # Boolean expression
                elif tokens_len > 2:
                    parse_result = self.parse_boolean(tokens[1:])
                    if parse_result in truefalse:
                        condition_execution_stack.append(parse_result)
                    else:
                        print "wtf can't imply this"
                        return

                # print condition_scope_stack, condition_execution_stack, line_count

            elif (tokens_len == 2) and (tokens[0] == "or") and (tokens[1] == "not") and (len(condition_scope_stack) > 0):
                condition_scope_stack[-1] = FALSE
                # print condition_scope_stack, condition_execution_stack, line_count

            elif tokens[0] == "inb4":
                if (tokens_len == 8) and (tokens[2] == "from") and (tokens[4] == "to") and (tokens[6] == "by"):
                    self.variables[tokens[1]] = int(tokens[3])
                    call_stack.append({"linepos": line_count,
                                      "counter": tokens[1],
                                      "start": int(tokens[3]),
                                      "end": int(tokens[5]),
                                      "step": int(tokens[7])})
                else:
                    print "wtf can't inb4 this"
                    return

            elif (tokens[0] == "done") and (tokens_len > 1):
                if tokens[1] == "inb4" and len(call_stack) > 0:
                    call = call_stack[-1]
                    self.variables[call["counter"]] += call["step"]
                    if (call["step"] > 0 and self.variables[call["counter"]] < call["end"]) \
                            or (call["step"] < 0 and self.variables[call["counter"]] > call["end"]):
                        line_count = call["linepos"]
                    else:
                        del self.variables[call["counter"]]
                        call_stack.pop()
                elif tokens[1] == "implying" and len(condition_scope_stack) > 0:
                    condition_scope_stack.pop()
                    condition_execution_stack.pop()
                    # print condition_scope_stack, condition_execution_stack, line_count

            else:
                print "wtf r u doing"
                return

            line_count += 1

    def main(self):
        inputlines = []

        for line in sys.stdin:
            strippedline = line.lstrip()
            if len(strippedline) > 0:
                if strippedline[0] != '>':
                    print "do you even greentext"
                    return
                else:
                    inputlines.append(strippedline[1:])

        self.parse(inputlines)


Parser().main()
