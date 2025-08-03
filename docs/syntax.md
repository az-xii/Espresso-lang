# Syntax Basics

## Notes
- Brace `{}` syntax is required in Espresso.
- Semicolons `;` are **optional** — treated as line terminators, but not required.
- Comments:
  - Single-line: `//`
  - Multi-line: `/* ... */`

---

## Operators

### Arithmetic Operators
```espresso
int a = 10
int b = 3

int sum = a + b          // 13
int diff = a - b         // 7
int product = a * b      // 30
float div = a / b        // 3.333...
int mod = a % b          // 1
```

### Comparison Operators

Only values of the same type can be compared.
```
int x = 5
int y = 10

bool eq = x == y         // False
bool neq = x != y        // True
bool gt = x > y          // False
bool lt = x < y          // True
bool gte = x >= y        // False
bool lte = x <= y        // True
```

### Logical Operators
```
bool a = True
bool b = False

bool andResult = a and b     // False
bool orResult = a or b       // True
bool notResult = not a       // False
```

- Espresso uses `and`, `or`, `not` instead of `&&`, `||`, `!` for clarity.

### Bitwise Operators
```
int a = 0b1100   // 12
int b = 0b1010   // 10

int lShift = a << 1       // 0b11000 = 24
int rShift = a >> 1       // 0b0110 = 6

int andBits = a & b       // 0b1000 = 8
int orBits = a | b        // 0b1110 = 14
int xorBits = a ^ b       // 0b0110 = 6

int notBits = ~a          // -13 (in two's complement)
```

 - Note: ~a returns the bitwise NOT of a 32-bit signed integer.

### String Concatenation
```
str first = "Hello"
str second = "World"

str result = first + " " + second     // "Hello World"
```

### Ternary Operator
```
int age = 20
str status = age >= 18 ? "adult" : "minor"     // "adult"

float price = 15.99
float final = price > 20 ? price * 0.8 : price // 15.99

str message = hasPermission() ? "Welcome!" : "Access denied"
```
- Nesting is supported but discouraged:
```
str category = age < 13 ? "child" : age < 20 ? "teen" : "adult"
```

### Access: . vs ::

- Use `.` to access instance members

- Use `::` to access static or namespaced members
```
class Entity {}

class Player : public Entity {
    static const int ENTITY_TYPE = 1

    public:
    func Player() {}
    func getType() -> int {
        return Player::ENTITY_TYPE  // Static access
    }
}

main:
    Player p()
    io::output(p.getType())        // Instance access
```