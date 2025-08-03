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
