# Espresso Programming Language - Documentation v2.1

- Espresso is a new programming language designed to combine the speed and memory management of C++ with the readability and ease of Python. The syntax is user-friendly, aiming to reduce complexity while providing the power of low-level programming.

## Syntax Basics

### Cases
Brace `{}` syntax is reqired in Espresso, but semicolons `;` at the end of lines is optional
```
int camelCase = 0

class PascalCase { func Pascal(){}}

func PascalCase::otherCamelCase() -> void { std::cout << "Hello, world!" << std::endl; }


```

### Comments
Espresso supports single-line and multi-line comments:

```espresso
// Single line comment

/*
    Multi-line comment
*/
```

### Operators

#### Arithmetic Operators
```espresso

int a = 10 
int b = 3 

int sum = a + b         # Addition (13)
int diff = a - b        # Subtraction (7)
int product = a * b     # Multiplication (30)
float div = a / b       # Division (3.333...)
int mod = a % b         # Modulo (1)
```

#### Comparison Operators
Only values of the same type can be compared:
```espresso
int x = 5 
int y = 10 

bool equal = x == y         # Equal to (False)
bool notEqual = x != y      # Not equal to (True)
bool greater = x > y        # Greater than (False)
bool less = x < y           # Less than (True)
bool greaterEq = x >= y     # Greater than or equal to (False)
bool lessEq = x <= y        # Less than or equal to (True)
```

#### Logical Operators
```espresso
bool a = True 
bool b = False 

bool andResult = a and b    # Logical AND (False)
bool orResult = a or b      # Logical OR (True)
bool notResult = not a      # Logical NOT (False)
```

#### Bitwise Operators
```espresso
int a = 0b1100      # 12 in decimal
int b = 0b1010      # 10 in decimal

int leftShift = a << 1      # Left shift (0b11000)
int rightShift = a >> 1     # Right shift (0b0110)
int bitwiseAnd = a & b      # Bitwise AND (0b1000)
int bitwiseOr = a | b       # Bitwise OR (0b1110)
int bitwiseXor = a ^ b      # Bitwise XOR (0b0110)
int bitwiseNot = ~a         # Bitwise NOT (0b0011)
```

#### String Concatenation
Strings are joined using the `+` operator:
```espresso
str first = "Hello";
str second = "World";
str result = first + " " + second;    # "Hello World"
```

#### Ternary Operator
```espresso
int age = 20;
str status = age >= 18 ? "adult" : "minor";    # "adult"

# Can be used with any compatible types
float price = 15.99;
float final = price > 20 ? price * 0.8 : price;   # 15.99

# Can use function calls
str message = hasPermission() ? "Welcome!" : "Access denied";

# Nesting is possible but discouraged for readability
str category = age < 13 ? "child" 
                : age < 20 ? "teen" 
                : "adult";
```

## Functions

### Function Declaration
Functions in Espresso use the following syntax:
```espresso
[modifiers] func name([parameters]) -> returnType:
    # Function body

```

Access modifiers and static keyword are optional:
```espresso
private func helper() -> void  
static func utility() -> int return 42; 
```

### Basic Functions
```espresso
import io;

# Return value
func add(int a, int b) -> int:
    return a + b;


# Void return
func greet(str name) -> void:
    io.output("Hello, " + name);


# Multiple parameters
func calculateArea(float length, float width) -> float:
    return length * width;

```

### Parameter Features
```espresso
# Default parameters
func greet(str name, str title="Mr.") -> void:
    io.output("Hello, " + title + " " + name);


# Named arguments
greet("Smith", title="Dr.");  # "Hello Dr. Smith"
greet("Jones");               # "Hello Mr. Jones"

# Variable arguments
func sum(int first, int... rest) -> int:
    int total = first;
    for (int num in rest): 
        total += num;
    
    return total;


sum(1);             # Returns 1
sum(1, 2, 3);       # Returns 6
```
### Dynamic Parameters
```
func debug(*any args) -> void:  # list[any]
    for any item in args:
        io.output(item);

debug(3.14, 42, "Hello")

func summarize(*str args) -> void:   # list[str]
    let result = "";
    for (item in args):
        result = result + item as str + ", ";
    io.output(result);

summarize(1, "apple", 3.14, Dog()); #1, apple, 3.14, Dog, 
```
### Expression Functions
Single-line functions use a more concise syntax:
```espresso
# Basic expression function
func double(int x) -> int : {return x * 2;}

# With condition
func isEven(int x) -> bool : {return x % 2 == 0;}

# With string operations
func capitalize(str s) -> str : {s.length() > 0 ? return s[0].toUpper() + s[1:] : return s;}
```

### Function Overloading
Functions can be overloaded based on parameter types and count:
```espresso
func process(int value) -> void:
    io.output("Processing integer: " + value);


func process(str value) -> void:
    io.output("Processing string: " + value);


func process(int x, int y) -> void:
    io.output("Processing two integers: " + x + ", " + y);


# Usage
process(42);                # "Processing integer: 42"
process("hello");           # "Processing string: hello"
process(1, 2);              # "Processing two integers: 1, 2"
```

### Lambda Functions
Anonymous functions for inline use:
```espresso
# Basic lambda
lambda(int x) -> int : x * x;

# Multi-parameter lambda
lambda(int x, int y) -> int : x + y;

# Lambda as parameter
func processItems(list[int] items, func(int) -> int transform) -> void:
    for (int item in items):
        io.output(transform(item));
    


# Usage with lambda
list[int] nums = [1, 2, 3];
processItems(nums, lambda(int x) -> int : x * 2);  # 2, 4, 6

# Lambda capturing variables
int multiplier = 10;
lambda(int x) -> int : x * multiplier;      # Captures multiplier from outer scope
```

### Function Types
Functions are first-class citizens and can be stored in variables:
```espresso
# Function type declaration
type MathFunc = func(int, int) -> int;

# Store function in variable
MathFunc add = func(int a, int b) -> int : return a + b;
MathFunc multiply = func(int a, int b) -> int : return a * b;

# Use function variable
int result1 = add(5, 3);        # 8
int result2 = multiply(5, 3);   # 15

# Function as parameter
func applyMath(int x, int y, MathFunc operation) -> int:
    return operation(x, y);

# Usage
int sum = applyMath(5, 3, add);             # 8
int product = applyMath(5, 3, multiply);    # 15
```

## Control Flow

### Selection Statements

#### If-Elif-Else
```espresso
import io;

# Basic if statement
if (condition):     #'()' not necessary
    # Code block

# If-else statement
if (condition):     #'()' not necessary
    # True block
 else:
    # False block


# If-elif-else chain
if (value < 0):
    io.output("Negative");
 elif (value > 0):
    io.output("Positive");
 else:
    io.output("Zero");
```

### Pattern Matching - OMITTED

```espresso
# Basic match expression
match (value):
    < 0:
        io.output("Negative");
    > 0:
        io.output("Positive");
    == 0:
        io.output("Zero");


# Match with type patterns
match (value): 
    is int:
        io.output("Integer: ${value}");
    is string:
        io.output("String: ${value}");
    is list:
        io.output("List of length ${value.length()}");
    _:
        io.output("Unknown type");


# Match with destructuring
match (point): 
    (0, 0):
        io.output("Origin");
    (x, 0):
        io.output("On X axis: ${x}");
    (0, y):
        io.output("On Y axis: ${y}");
    (x, y):
        io.output("Point: (${x}, ${y})");


# Match expressions with guards
match (age, hasLicense):
    (a, true) if a >= 18:
        io.output("Can drive");
    (a, _) if a >= 18:
        io.output("Can apply for license",);
    _:
        io.output("Too young to drive");

```

### Loop Statements

#### For Loop
```espresso
# Basic for loop
for (int i in 0..<10):
    io.output(i);

# For loop with custom increment
for (int i in 0..<10:2):
    io.output(i);   # 0, 2, 4, 6, 8

```

#### For-In Loop
```espresso
# Iterate over list
list[int] numbers = [1, 2, 3, 4, 5];
for (int num in numbers):
    io.output(num);

# Iterate over map entries
map[str, int] scores = {
    "Alice": 95,
    "Bob": 87,
    "Charlie": 92
};

for (str name, int score in scores.pairs()):
    io.output(name + ": " + score);

```

#### While Loop
```espresso
# Basic while loop
int count = 0;

while (count < 5):
    io.output(count);
    count += 1;     # 1, 2, 3, 4

```

### Control Statements

#### Break and Continue
```espresso
# Break example
for int i in 0..<10:
    if i == 5:
        break;  # Exit loop
    
    io.output(i);


# Continue example
for int i in 0..<5:
    if i % 2 == 0:
        continue;  # Skip even numbers
    
    io.output(i);  # Print odd numbers

```

#### Return Statement
```espresso
func findFirst(list[int] numbers, int target) -> int:
    for (int i = 0, i < numbers.length()):
        if (numbers[i] == target):
            return i;  # Early return
        
    return -1;  # Not found

```

## Classes and Objects

### Class Declaration
```espresso
class Person:
    public:
    # Constructor
        func __init__(str name, int age) -> void:
            this.name = name;
            this.age = age;
        

        # Getter
        func getName() -> str:
            return this.name;
        

        # Setter with validation
        func setAge(int newAge) -> void:
            if (newAge >= 0):
                this.age = newAge;
            
        

        # Static method
        static func fromBirthYear(int year) -> Person:
            int age = getCurrentYear() - year;
            return new Person("Unknown", age);
        

    # Private fields
    private:
        str name;
        int age;


# Creating instances
Person john = new Person("John", 30);
Person someone = Person.fromBirthYear(1990);
```

### Special Methods (Dunder Methods)

```espresso
class Vector2D:
    public:
        float x;
        float y;

        # Constructor
        func __init__(float x, float y) -> void:
            this.x = x;
            this.y = y;
        

        # String representation
        func __str__() -> str : return "Vector2D(${this.x}, ${this.y})";
        
        # Debug representation
        func __repr__() -> str : return "Vector2D(x=${this.x}, y=${this.y})";

        # Arithmetic operators
        func __add__(Vector2D other) -> Vector2D:
            return new Vector2D(this.x + other.x, this.y + other.y);
        
        func __sub__(Vector2D other) -> Vector2D:
            return new Vector2D(this.x - other.x, this.y - other.y);
        
        func __mul__(float scalar) -> Vector2D:
            return new Vector2D(this.x * scalar, this.y * scalar);

        func __div__(float scalar) -> Vector2D:
            return new Vector2D(this.x / scalar, this.y / scalar) if (scalar != 0) else throw ValueError("Division by zero");

        func __fdiv__(float scalar) -> Vector2D:
            if (scalar == 0):
                throw ValueError("Division by zero");
            return new Vector2D(this.x / scalar, this.y / scalar);

        # Incriment
        func __iadd__(Vector2D other) -> Vector2D:
            return new Vector2D(this.x + other.x, this.y + other.y);

        func __iadd__(tuple[float, float] incx incy) -> Vector2D:
            return new Vector2D(this.x + incx, this.y + incy);

        func __isub__(Vector2D other) -> Vector2D:
            return new Vector2D(this.x - other.x, this.y - other.y);

        func __isub__(tuple[float, float] incx incy) -> Vector2D:
            return new Vector2D(this.x - incx, this.y - incy);

        func __imul__(Vector2D other) -> Vector2D:
            return new Vector2D(this.x * other.x, this.y * other.y);

        func __imul__(tuple[float, float] incx incy) -> Vector2D =
            return new Vector2D(this.x * incx, this.y * incy);

        func __idiv__(Vector2D other) -> Vector2D:
            return new Vector2D(this.x / other.x, this.y / other.y);

        func __idiv__(tuple[float, float] incx incy) -> Vector2D:
            return new Vector2D(this.x / incx, this.y / incy);


        # Comparison
        func __eq__(Vector2D other) -> bool:
            return this.x == other.x and this.y == other.y;

        # Type conversion
        func __float__() -> float: return sqrt(this.x**2 + this.y**2);
        func __bool__() -> bool: return this.x != 0 or this.y != 0;


# Usage
Vector2D v1 = new Vector2D(1.5, 2.5);
Vector2D v2 = new Vector2D(3.0, 4.0);
io.output(v1 + v2);      # "Vector2D(4.5, 6.5)"
float mag = v1 as float; # 2.915 (magnitude)
```

### Access Control
Espresso uses three visibility levels:

```espresso
class Example:
    public:
        # Accessible from anywhere
        int publicField;
        func publicMethod() -> void  

    protected:
        # Accessible in this class and its subclasses
        int protectedField;
        func protectedMethod() -> void  

    private:
        # Only accessible within this class
        int privateField;
        func privateMethod() -> void  

```

### Inheritance
```espresso
# Base class
class Animal:
    public:
        func __init__(str name) -> void 
            this.name = name;
        

        # Virtual method that can be overridden
        virtual func makeSound() -> void 
            io.output("Generic animal sound");
        

    protected:
        str name;


# Derived class
class Dog(Animal):
    public:
        func Dog(str name, str breed) -> void 
            super(name);  # Call parent constructor
            this.breed = breed;
        

        # Override base class method
        override func makeSound() -> void 
            io.output("Woof!");
        

    private:
        str breed;


# Usage
Dog spot = new Dog("Spot", "Labrador");
spot.makeSound();  # Outputs: "Woof!"
```


### Static Members
```espresso
class MathUtils:
    # Static constant
    static const float PI = 3.14159;

    # Static method
    static func square(float x) -> float:
        return x * x;

    # Static property
    static func getInstanceCount() -> int:
        return instanceCount;

    static func setInstanceCount(int val) -> void:
        instanceCount = val;

    # Static variable
    private static int instanceCount = 0;

# Usage
float area = MathUtils.PI * radius * radius;
float squared = MathUtils.square(5);
int count = MathUtils.getInstanceCount();
MathUtils.setInstanceCount(10);

```

CHANGED TO:
```espresso
@static
class MathUtils:
    # Static constant
    @static
    @const
    float PI = 3.14159;

    # Static method
    @static
    func square(float x) -> float:
        return x * x;

    # Static property
    func getInstanceCount() -> int:
        return instanceCount;

    func setInstanceCount(int val) -> void:
        instanceCount = val;

    # Static variable
    private static int instanceCount = 0;
```

## Types and Type Casting

### Core Types

#### Numeric Types
```espresso
# Signed integers
int d = 2_147_483_647;  # 32-bit
long e = 9e18;           # 64-bit

# Unsigned integers
u32 ip = 0xC0A80101;    # 32-bit unsigned
u64 big = 0xFFFF_FFFF;  # 64-bit unsigned

# Floating point;
float pi = 3.14159;       # 32-bit fixed decimal
double precise = 1.0e-15;  # 64-bit fixed decimal
decimal money = 129.99; # 128-bit fixed decimal

# Literal formats
bin mask = 0b1010_1100;
hex color = 0xFF_00_80_FF;
oct perm = 0o755
```

#### Text Types
```espresso
# Character type (single quotes, '...')
char a = 'a';
char tab = '\t';
char unicode = '\u0041';

# String type (double quotes, "...")
str name = "Alice";
str path = "C:\\Program Files\\Espresso";  # Escaped backslash
str raw = r"C:\Program Files\Espresso";    # Raw string
str interpolated = "Hello, ${name}!";  # Interpolation
```

#### Container Types
```espresso
# Lists - ordered, mutable sequences of homogenous elements
list[int] numbers = [1, 2, 3];

# Sets - unique, unordered elements
set[str] uniqueNames = {"Alice", "Bob"};

# Maps - key-value pairs
map[str, int] ages = {
    "Alice": 25,
    "Bob": 30
};

# Tuple - ordered, immutable sequence of hetrogenous values
tuple[int, str] pair = (42, "hello");
int pair_int, str pair_string = pair
```

#### Miscellaneous Types
```espresso
# void - the absence of value. All variables can be voided
int num = void;
num = 1;

# auto - type inference, useful for more complex types
auto temperature = 98.6;    # float
auto user = User("Alice");  # User

auto players = {
    "player1": 1,
    "player2": 2,
    "player3": 3
};  # map[str, int]

# any - no fixed type
any changeable = 1
changeable = 'h'
changeable = "i can be anything!"
```


### Type Casting

#### Using the `as` Operator
```espresso
# Primitive type casting
int num = 42;
str num_str = num as str;       # "42"
float exact = num as float;     # 42.0

# Container casting
list[int] nums = [1, 2, 2, 3];
set[int] unique_nums = nums as set;  # 1, 2, 3

# Custom type casting
class Temperature 
    public:
        func __init__(float celsius) -> void  
            this.c = celsius; 
        
        
        func __float__() -> float
            return this.c;

        func __str__() -> str
            return "${this.c}°C";


Temperature temp = new Temperature(25.5);
float celsius = temp as float;  # 25.5 (calls __float__)
str display = temp as str;      # "25.5°C" (calls __str__)

```

#### Implicit Casting
```espresso
# Safe conversions happen automatically
int small = 42;
int32 medium = small;      # int -> int32
int64 large = medium;      # int32 -> int64
float f = small;          # int -> float

```

#### Explicit Casting
```espresso
# Potentially unsafe conversions require explicit cast
float pi = 3.14159;
int rounded = pi as int;        # float -> int (3)

# Container conversions
list[int] numbers = [1, 1, 2, 3];
set[int] unique = numbers as set;  # Creates set 1, 2, 3

```

## String Manipulation

### Basic String Operations
```espresso
str text = "Hello, World!";

# Length and access
int length = text.length();         # 13
char first = text[0];               # 'H'
char last = text[-1];               # '!'

# Slicing
str slice = text[0:5];           # "Hello"
str end = text[-6:];             # "World!"
str every2 = text[::2];          # "Hlo ol!"

# Case conversion
str upper = text.toUpper();      # "HELLO, WORLD!"
str lower = text.toLower();      # "hello, world!"

```

### String Concatenation and Interpolation
```espresso
# String concatenation with `+`
str first = "Hello";
str second = "World";
str greeting = first + " " + second;  # "Hello World"

# Simple interpolation
str name = "Espresso";
str version = "2.0";
str info = "Welcome to ${name} v${version}!";

# Complex interpolation
float price = 19.99;
int quantity = 3;
str total = "Total: $${price * quantity}";  # "Total: $59.97"

```

### String Functions
```espresso
str text = "  Hello, World!  ";

# Basic operations
str trimmed = text.trim();              # "Hello, World!"
list[str] parts = text.split(",");      # ["  Hello", " World!  "]
bool starts = text.startsWith("  Hello");   # True
bool ends = text.endsWith("!  ");          # True

# Searching
int pos = text.indexOf("World");           # 8
bool contains = text.contains("Hello");     # True

# Replacing
str new = text.replace("World", "Espresso");  # "  Hello, Espresso!  "

```

## Container Manipulation

### Built-in Container Operations

```espresso
# List operations
list[int] numbers = [1, 2, 3];
numbers.append(4);                # [1, 2, 3, 4]
numbers.prepend(0);              # [0, 1, 2, 3, 4]
numbers.insert(2, 5);            # [0, 1, 5, 2, 3, 4]
numbers.remove(1);               # [0, 5, 2, 3, 4]
numbers.removeAt(0);             # [5, 2, 3, 4]
int length = numbers.length();    # 4
list[int] a = [1, 2, 3];
list[int] b = [3, 4, 5];
list[int] combined = a or b;         # [1, 2, 3, 4, 5] (union-like, no dedup)
list[int] shared = a and b;          # [3] (intersection)
list[int] removed = a - b;           # [1, 2]


# Set operations
set[int] setA = 1, 2, 3;
set[int] setB = 3, 4, 5;
set[int] union = setA or setB;        # 1, 2, 3, 4, 5
set[int] intersect = setA and setB;    # 3
set[int] diff = setA - setB;         # 1, 2
bool has3 = setA.contains(3);        # True

# Map operations
map[str, int] ages = 
    "Alice": 25,
    "Bob": 30
;
ages["Charlie"] = 35;              # Add new key-value pair
ages.remove("Bob");                # Remove entry
bool hasAlice = ages.hasKey("Alice");  # True
tuple[str...] keys = ages.keys();   # ("Alice", "Charlie")
tuple[int...] values = ages.values();  # (25, 35)

# Tuple operations
int length = player.length();  # 2
bool equals = a.equals(b);     # False
str string = a as str # "(1, 2)"

int start = exclusiveRange.start;   # 0
int end = inclusiveRange.end;       # 10
int step = steppedRange.step;       # 2

```

### Container Views and Slices
Efficient ways to work with container subsets:

```espresso
# Slicing only 
list[int] numbers = [0, 1, 2, 3, 4, 5];
list[int] view = numbers[1:4];              # [1, 2, 3]
list[int] steps = numbers[::2];             # [0, 2, 4]
list[int] reversed = numbers[::-1];         # [5, 4, 3, 2, 1, 0]

# Map views
map[str, int] scores = "Alice": 95, "Bob": 87, "Charlie": 92;
list[tuple[str, int]] pairs = scores.pairs();  # [("Alice", 95), ("Bob", 87), ...]

```



## Error Handling

Espresso provides comprehensive error handling through exceptions and assertions.

### Try-Catch Blocks

Basic error handling uses try-catch blocks:

```espresso
try 
    # Code that might throw an error
    int result = someRiskyOperation();
 catch (ValueError e) 
    # Handle specific error types
    io.output("Invalid value: " + e.message);
 catch (Error e) 
    # Handle general errors
    io.output("Error occurred: " + e.message);
 finally 
    # Always executed, regardless of errors
    cleanupResources();

```

### Custom Errors

You can define custom error types by extending the base `Error` class:

```espresso
class DatabaseError(Error)
    public:
        func DatabaseError(str message) -> void 
            super(message);
        


class ConnectionError(DatabaseError)
    public:
        func ConnectionError(str message, int errorCode) -> void 
            super("Connection failed: " + message);
            this.errorCode = errorCode;
        
    
    private:
        int errorCode;


# Using custom errors
func connectToDatabase(str url) -> void 
    if (not isValidUrl(url)) 
        throw ValueError("Invalid database URL");
    
    if (not hasConnection()) 
        throw ConnectionError("Could not connect to " + url, 404);
    
```

### Assert Statement

Assertions are used for debugging and development-time checks:

```espresso
func divide(float a, float b) -> float 
    assert(b != 0, "Division by zero!");
    return a / b;


func processAge(int age) -> void 
    assert(age >= 0 and age <= 150, "Age must be between 0 and 150");
    # Process age...

```

### Built-in Error Types

Espresso provides several built-in error types:

```espresso
# Common error types
throw Error("Generic error");
throw ValueError("Invalid value");
throw TypeError("Type mismatch");
throw IndexError("Index out of bounds");
throw KeyError("Key not found");
throw NotImplementedError("Feature not implemented");

```

### Error Propagation

Errors automatically propagate up the call stack:

```espresso
func validateUser(str username) -> void:
    # Throws error if validation fails
    if (not isValid(username)):
        throw ValueError("Invalid username");
    


func createUser(str username) -> void 
    try:
        validateUser(username);  # Error from validateUser propagates
        # Create user...
     catch (ValueError e):
        # Handle validation error
        io.output("Could not create user: " + e.message);

```

## Standard Library

### `import io;`
```espresso
#* Open codes:
io.FileAccess.Read
io.FileAccess.Write
io.FileAccess.Append
io.FileAccess.ReadWrite
*#

# File Ops
io.File file = io.open("data.txt", io.FileAccess.ReadWrite);  # Throws IOError on failure

str content = file.read();          # Read entire file
list[str] lines = file.readLines(); # Read as lines
file.write("Hello\n");                 # Write string
file.writeLines(["Line1", "Line2"]);   # Write lines

bin data = file.readBytes();           # Read raw bytes
file.writeBytes(0x48_65_6C_6C_6F);    # Write hex bytes

file.close();                          # Always close!

# Path Manipulation

str path = io.join("dir", "file.txt");  # Platform-aware joining
str abs_path = io.absPath("file.txt");  # Absolute path
str parent = io.dirname(r"/path/to/file"); 
str filename = io.basename(r"/path/to/file.txt");  # "file.txt"
str ext = io.getExt("file.txt");   # ".txt"


# File System Ops

# File tests
bool exists = io.exists("file.txt");
bool is_file = io.isfile("file.txt");
bool is_dir = io.isdir("mydir");
int size = io.getsize("file.txt");     # Bytes

# Operations
io.copy("src.txt", "dest.txt");        # Throws if exists
io.move("old.txt", "new.txt");         # Rename/move
io.delete("file.txt");                 # Throws if missing
io.mkdir("newdir");                    # Create directory
list[str] files = io.listdir(".");  # List contents

# JSON Ops

io.JSON json = io.openJson("data.json");

map[any, any] json_data = json.load();

map[any, any] new_data = {
  "name": "John",
  "age": 30,
  "married": True,
  "divorced": False,
  "children": ("Ann","Billy"),
  "pets": None,
  "cars": [
    {"model": "BMW 230", "mpg": 27.5},
    {"model": "Ford Edge", "mpg": 24.1}
  ]
};

json.dump(new_data, indent=4);

```

### `import math;`

```espresso
# Constants
math.PI;        # 3.141592653589793
math.TAU;       # 6.283185307179586 (2π)
math.E;         # 2.718281828459045 (Euler's number)
math.INF;       # Infinity
math.NAN;       # Not a Number
math.PHI;       # 1.618033988749895 (Golden ratio)

# Configuration
math.set_precision(16);      # Set decimal places (default: 16)
math.set_angle(math.Angles.Degrees);    # .Radians or .Degrees (default: Degrees)

# Utility

math.abs(x);            # Absolute value
math.ceil(x);           # Smallest integer ≥ x
math.floor(x);          # Largest integer ≤ x
math.round(x, n=0);     # Round to n decimal places
math.trunc(x);          # Truncate toward zero

math.erf(x);           # Error function
math.gamma(x);         # Gamma function
math.factorial(x);     # x! (integer only)

# Logs and Exponents

math.exp(x);            # e^x
math.pow(x, y);         # x^y
math.sqrt(x);           # Square root x
math.cbrt(x);           # Cube root x
math.root(x, y);        # x root y
math.log(x, y);         # Log x base y, base = math.E by default
math.log2(x);           # Log x base 2
math.log10(x);          # Log x base 10

# Random

math.random();              # Float in 0.0..=1.0
math.randint(a, b);         # Integer in a..=b
math.uniform(a, b);         # Float in a..=b
math.choice([...items]);    # Random item from sequence
math.shuffle([...mut_list]); # Shuffle mutable list in-place

# Statistics

math.sum([...numbers]);  # Sum of iterable
math.prod([...numbers]); # Product of iterable
math.avg([...numbers]);  # Arithmetic mean
math.median([...numbers]); # Median
math.gcd(a, b);         # Greatest common divisor
math.lcm(a, b);         # Least common multiple
math.comb(n, k);        # Combinations (n choose k)
math.perm(n, k);        # Permutations (n!/(n-k)!)

# Trigonometry

math.sin(x);            # Sine
math.cos(x);            # Cosine
math.tan(x);            # Tangent
math.asin(x);           # Arcsine
math.acos(x);           # Arccosine
math.atan(x);           # Arctangent
math.atan2(y, x);       # Arctangent of y/x (proper quadrant)
math.hypot(x, y);       # sqrt(x² + y²) (Euclidean norm)

math.sinh(x);           # Hyperbolic sine
math.cosh(x);           # Hyperbolic cosine  
math.tanh(x);           # Hyperbolic tangent

math.degrees(x);        # Radians → Degrees
math.radians(x);        # Degrees → Radians

```


## Comprehensive Example Script

Below is a full-featured Espresso script demonstrating variables, types, functions, classes, inheritance, control flow, containers, error handling, pattern matching, and standard library usage.

```espresso
import io;
import math;

# Variables and types
int a = 10;
float b = 3.5;
decimal price = 19.99;
str name = "Espresso";
bool isActive = true;
bin mask = 0b1010_1100;
hex color = 0xFF00FF;
oct perm = 0o755;

# String interpolation and concatenation
str greeting = "Hello, ${name}! Your price is $${price}";
io.output(greeting);

# Lists, sets, maps, tuples
list[int] nums = [1, 2, 3, 4, 5];
set[str] tags = {"alpha", "beta"};
map[str, int] scores = {
    "Alice": 95,
    "Bob": 87
};
tuple[int, str] pair = (42, "answer");

# Functions, overloading, lambdas, function types
func add(int x, int y) -> int:
    return x + y;

func add(float x, float y) -> float:
    return x + y;

type MathFunc = func(int, int) -> int;
MathFunc multiply = lambda(int x, int y) -> int : x * y;
int prod = multiply(4, 5);
Mathfunc square = func(int x) -> int : return x * x;

# Control flow: if, elif, else, ternary
for int n in nums:
    if n % 2 == 0:
        io.output("${n} is even");
    elif n == 3:
        io.output("Three!");
    else:
        io.output("${n} is odd");

str status = prod > 10 ? "big" : "small";
io.output("Product is ${status}");

# While loop
int i = 0;
while i < 3:
    io.output("i = ${i}");
    i += 1;

# Pattern matching
int value = -1;
match (value):
    < 0:
        io.output("Negative");
    == 0:
        io.output("Zero");
    > 0:
        io.output("Positive");

# Classes, inheritance, static, visibility
class Animal:
    public:
        str name;
        func __init__(str name) -> void:
            this.name = name;
        func speak() -> str : return "???";

class Dog(Animal):
    public:
        func __init__(str name) -> void:
            super(name);
        override func speak() -> str : return "Woof!";

Dog d = new Dog("Spot");
io.output(d.speak());

# Static members
class MathUtils:
    static func square(int x) -> int : return x * x;
    static const float PI = 3.14159;

int sq = MathUtils.square(7);
float area = MathUtils.PI * 2 * 2;

# Access control
class Example:
    public:
        int pubField;
    private:
        int privField;
    protected:
        int protField;

# Error handling
try:
    int x = 10 / 0;
catch (Error e):
    io.output("Caught error: " + e.message);
finally:
    io.output("Done error handling");

# Container operations
nums.append(6);
nums.remove(1);
set[int] odds = {1, 3, 5};
set[int] union = odds or nums as set;
scores["Charlie"] = 88;

# String manipulation
str text = "Hello, World!";
str upper = text.toUpper();
str slice = text[0:5];

# Type casting and assertions
float f = 42 as float;
str s = f as str;
func safeDiv(int a, int b) -> float:
    assert(b != 0, "Division by zero!");
    return a / b;

io.output("All features demoed!") 
```
