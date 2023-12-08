from types import NoneType
from typing import Union

from scanner import Scanner, Token, TokenType

JsonValue = Union["JsonObject", "JsonArray", str, int, float, bool, NoneType]
JsonObject = dict[str, JsonValue]
JsonArray = list[JsonValue]


def parse(input: str) -> JsonValue:
    scanner = Scanner(input)
    tokens = scanner.scan()
    parser = Parser(tokens)
    return parser.parse()


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> JsonValue:
        token = self.advance()
        return self.parse_from_token(token)

    def parse_from_token(self, token: Token) -> JsonValue:
        match token.token_type:
            case TokenType.STRING | TokenType.NUMBER | TokenType.BOOLEAN | TokenType.NULL:
                return token.value
            case TokenType.LEFT_BRACE:
                return self.parse_object()
            case TokenType.LEFT_BRACKET:
                return self.parse_array()
            case _:
                raise ValueError("Unexpected token", token)

    def parse_object(self) -> JsonObject:
        json_object = {}

        key_token = self.advance()
        while key_token.token_type != TokenType.RIGHT_BRACE:
            if key_token.token_type == TokenType.EOF:
                raise ValueError("Unterminated JSON object")

            if key_token.token_type != TokenType.STRING:
                raise ValueError('JSON object fields must begin with a "key"')

            self.consume(TokenType.COLON, "Key: values must be colon separated")

            value_token = self.advance()
            json_object[key_token.value] = self.parse_from_token(value_token)

            self.consume_comma_unless(TokenType.RIGHT_BRACE)
            key_token = self.advance()

        return json_object

    def parse_array(self) -> JsonArray:
        json_array = []

        token = self.advance()
        while token.token_type != TokenType.RIGHT_BRACKET:
            if token.token_type == TokenType.EOF:
                raise ValueError("Unterminated JSON array")

            json_array.append(self.parse_from_token(token))

            self.consume_comma_unless(TokenType.RIGHT_BRACKET)
            token = self.advance()

        return json_array

    def advance(self) -> Token:
        token = self.tokens[self.current]
        self.current += 1
        return token

    def consume(self, token_type: TokenType, error: str):
        if self.peek().token_type != token_type:
            raise ValueError(error)

        self.current += 1

    def consume_comma_unless(self, exception: TokenType):
        if self.peek().token_type == TokenType.COMMA:
            # We allow trailing commas
            self.advance()
            return

        if self.peek().token_type != exception:
            raise ValueError("Missing comma unless followed by", str(exception))

    def peek(self) -> Token:
        return self.tokens[self.current]
