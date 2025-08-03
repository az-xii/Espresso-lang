## Types and Type Casting

### Core Types

#### Numeric Types
- Note: Suffixes arent strictly necessary
```espresso
// Signed integers
byte b = 0xFFb              // 8-bit signed
short s = 0x7FFFs           // 16-bit signed
int d = 2_147_483_647i      // 32-bit signed (default)
long e = 9_000_000_000_000l // 64-bit signed
longlong nonce = 1.4e20ll      // 128-bit signed

// Unsigned integers
ubyte ub = 0xFFub           // 8-bit unsigned
ushort us = 65535us         // 16-bit unsigned
uint ip = 0xC0A80101u       // 32-bit unsigned
ulong big = 0xFFFF_FFFFul   // 64-bit unsigned
ulonglong ultra = 1ull      // 128-bit unsigned

// Floating point
float pi = 3.14159f         // 32-bit float
double precise = 1.0e-15    // 64-bit float (default)
decimal money = 129.99m     // 128-bit decimal

// Fixed-point (Q format)
fixed1616 ratio = 1fx16     // 16.16 fixed-point
fixed3232 smooth = 0.75fx   // 32.32 fixed-point
ufx1616 percent = 100ufx1616// Unsigned 16.16
```

#### Text Types
```espresso
// Character type (single quotes, '...')
char a = 'a' 
char tab = '\t' 
char unicode = '\u0041' 

// String type (double quotes, "...")
str name = "Alice" 
str path = "C:\\Program Files\\Espresso"    // Escaped backslash
str raw = r"C:\Program Files\Espresso"      // Raw string
str interpolated = $"Hello, {name}!"    // Interpolation
```

#### Container Types
```espresso
// Lists - ordered, mutable sequences of homogenous elements
list<int> numbers = [1, 2, 3] 

// Sets - unique, unordered elements
set<str> uniqueNames = {"Alice", "Bob"} 

// Maps - key-value pairs
map<str, int> ages = {
    "Alice": 25,
    "Bob": 30
} 

// Tuple - ordered, immutable sequence of hetrogenous values
tuple<int, str> pair = (42, "hello") 
int pair_int, str pair_string = pair
```

#### Miscellaneous Types
```espresso
// void - the absence of value. All variables can be voided
int? num = void 
num = 1 

// auto - type inference, useful for more complex types
auto temperature = 98.6      // float
auto user = User("Alice")    // User

auto players = {
    "player1": 1,
    "player2": 2,
    "player3": 3
}    // map[str, int]

// any - no fixed type
any changeable = 1

changeable = 'h'
changeable = "i can be anything!"
```


### Type Casting

#### Using the `as` Operator
```espresso
# Primitive type casting
int num = 42 
str num_str = num as str         // "42"
float exact = num as float       // 42.0

# Container casting
list[int] nums = [1, 2, 2, 3] 
set[int] unique_nums = nums as set    // 1, 2, 3

# Custom type casting
class Temperature
    float c

    public:
    func Temperature(float celsius) {
        this.c = celsius
    }
    @cast(float) -> float {
        return this.c 
    }
    @cast(str) -> str {
        return $"{this.c}°C" 
    }

main:
    Temperature temp = new Temperature(25.5) 
    float celsius = temp as float    // 25.5 (calls @cast(float))
    str display = temp as str        // "25.5°C" (calls @cast(str))
```

#### Implicit Casting
```espresso
# Safe conversions happen automatically
short small = 42 
int medium = small        // short -> int
long large = medium        // int -> long
float f = small            // short -> float
```

#### Explicit Casting
```espresso
# Potentially unsafe conversions require explicit cast
float pi = 3.14159 
int rounded = pi as int          // float -> int (3)

# Container conversions
list[int] numbers = [1, 1, 2, 3] 
set[int] unique = numbers as set    // Creates set 1, 2, 3
```