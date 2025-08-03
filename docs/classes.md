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
