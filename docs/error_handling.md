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
