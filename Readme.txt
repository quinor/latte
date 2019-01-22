ASSUMPTIONS TAKEN:

SYNTAX
    *   no "," operator, comma only used as a separator in function arguments, calls etc
    *   no ";" as an empty statement - instead of if(...); write if(){}
    *   ANY instr after return unreachable thus error
    *   if-if-else ambiguity: if(...) if(...) unallowed, requires braces for the top if
    *   spaces preferred over tabs - tabs interfere with pretty print of compiler errors
    *   Sadly no escape sequences for strings


SEMANTICS
    *   variables without initialization receive default initialization - if one cannot be
        inferred, that's an error
    *   There are no string compares besides == and !=

RUNTIME
    *   readString() reads only up to 1000 characters and reads a whitespace-separated string,
        not a line - TODO fix
