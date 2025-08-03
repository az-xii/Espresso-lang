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
