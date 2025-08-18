#! venv/bin/python
from test import Lexer

sourcecode: str  = r"""
// ==== Level 6. C++ interop ====

@include <iostream>
@using namespace std
@cpp {
    // Pure C++. Need C++ syntax, not Espresso
    bool is_prime(int n) {
        if n < 2 {
            return false;
        }
        for int i = 2; i <= int(math::sqrt(n)); i+=1 {
            if n % i == 0 {
                return false;
            }
        }
        return true;
    }
}

main: 
    list<int> primes = []

    for int num = 0, num < 50, num += 1 {
        if is_prime(num) {
            primes.append(num)
        }
    }

    cout << $"Primes under 50: {primes.Join(", ")}" << endl

    return 0
"""

tokens, cpp = Lexer.lex_tokens(source=sourcecode)
Lexer.pretty_print_tokens(tokens)

