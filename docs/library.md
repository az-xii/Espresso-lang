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

