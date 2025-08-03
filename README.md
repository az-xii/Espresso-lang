# Espresso Programming Language - Documentation v2.1

- Espresso is a new programming language designed to combine the speed and memory management of C++ with the readability and ease of Python. The syntax is user-friendly, aiming to reduce complexity while providing the power of low-level programming.

## Why Espresso?

## Getting started

## "Hello, world!"
```
@include "io"

class Greeter {
    func Greeter() {}

    func sayHello() {
        io::output("Hello, world!")
    }
}

main:
    Greeter g = Greeter()
    g.sayHello()

```

## Documentation

| File                    | Description                                            |
| ----------------------- | ------------------------------------------------------ |
| `docs/syntax.md`        | Syntax rules (braces, semicolons, comments, naming)    |
| `docs/types.md`         | Static types, `auto`, `any`, generics, nullable types  |
| `docs/functions.md`     | Functions, return types, overloads                     |
| `docs/classes.md`       | Classes, constructors, inheritance, access modifiers   |
| `docs/errors.md`        | Errors, `try`, `catch`, `else` and `throw`             |
| `docs/strings.md`       | Strings, `$"..."`, formatting                          |
| `docs/containers.md`    | Container manipulation, unions and intersects          |
| `docs/io.md`            | `io::output`, file access, interop with `std::cout`    |
| `docs/control.md`       | `if`, `switch`, `for`, ranges                          |
| `docs/modules.md`       | `@include`, custom module resolver                     |
| `docs/cpp_interop.md`   | Using raw C++, headers, STL                            |
| `docs/build.md`         | Running vs compiling, CLI options for micrcocontrollers|



