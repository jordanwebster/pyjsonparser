from enum import StrEnum, auto
from typing import Any


class TokenType(StrEnum):
    STRING = auto()
    NUMBER = auto()
    BOOLEAN = auto()
    NULL = auto()

    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    LEFT_BRACKET = auto()
    RIGHT_BRACKET = auto()
    COMMA = auto()
    COLON = auto()
    EOF = auto()


class Token:
    def __init__(self, token_type: TokenType, value: Any):
        self.token_type = token_type
        self.value = value


class Scanner:
    tokens: list[Token]

    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.tokens = []
        self.current = 0
        self.line = 1

    def scan(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, None))
        return self.tokens

    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_token(self):
        c = self.advance()
        match c:
            case "{":
                self.tokens.append(Token(TokenType.LEFT_BRACE, c))
            case "}":
                self.tokens.append(Token(TokenType.RIGHT_BRACE, c))
            case "[":
                self.tokens.append(Token(TokenType.LEFT_BRACKET, c))
            case "]":
                self.tokens.append(Token(TokenType.RIGHT_BRACKET, c))
            case ",":
                self.tokens.append(Token(TokenType.COMMA, c))
            case ":":
                self.tokens.append(Token(TokenType.COLON, c))
            case "\n":
                self.line += 1
            case " ":
                pass
            case '"':
                self.add_string()
            case "-":
                if self.peek().isdigit():
                    self.advance()
                    self.add_number()
                else:
                    raise ValueError("- must be followed by a number")
            case _:
                if c.isdigit():
                    self.add_number()
                elif c.isalpha():
                    self.add_keyword()
                else:
                    raise ValueError("Unexpected token", c, self.line)

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def add_string(self):
        while self.peek() != '"' and not self.is_at_end():
            self.advance()

        if self.is_at_end():
            raise ValueError("Unterminated string", self.line)
        # Consume the closing "
        self.advance()

        self.tokens.append(
            Token(TokenType.STRING, self.source[self.start + 1 : self.current - 1])
        )

    def add_number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == ".":
            if not self.peek_next().isdigit():
                raise ValueError("Expected digit after . (trying to parse float)")
            # Consume the .
            self.advance()

            while self.peek().isdigit():
                self.advance()

            self.tokens.append(
                Token(TokenType.NUMBER, float(self.source[self.start : self.current]))
            )
        else:
            self.tokens.append(
                Token(TokenType.NUMBER, int(self.source[self.start : self.current]))
            )

    def add_keyword(self):
        while self.peek().isalpha():
            self.advance()

        keyword = self.source[self.start : self.current]
        match keyword:
            case "true":
                token = Token(TokenType.BOOLEAN, True)
            case "false":
                token = Token(TokenType.BOOLEAN, False)
            case "null":
                token = Token(TokenType.NULL, None)
            case _:
                raise ValueError("Unexpected token", self.line, keyword)

        self.tokens.append(token)

    def peek(self) -> str:
        if self.is_at_end():
            return ""

        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return ""

        return self.source[self.current + 1]
