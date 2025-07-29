// Core/espresso_types/forward_decls.hpp
#pragma once
#include <exception>
// Forward declare integer types
class EspressoByte;
class EspressoShort;
class EspressoInt;
class EspressoLong;
class EspressoLongLong;

class EspressoUByte;
class EspressoUShort;
class EspressoUInt;
class EspressoULong;
class EspressoULongLong;

// Forward declare floating-point types
class EspressoFloat;
class EspressoDouble;
class EspressoDecimal;

// Forward declare fixed-point types
class EspressoFixed16_16;
class EspressoFixed32_32;
class EspressoUFixed16_16;

// Forward declare special types
class EspressoBool;
class EspressoVoid;
class EspressoNullptr;

// Forward declare character type
class EspressoChar;

// Forward declare string type
class EspressoString;

// Forward declare exception types
class Error : public std::exception { /* Base for all errors */ };
class RuntimeError : public Error { /* Base for runtime issues */ };
class LogicError : public Error { /* Programmer mistakes */ };

// Forward declare arithmetic exceptions
class DivisionByZeroError : public RuntimeError {};  // x / 0
class ModuloByZeroError : public RuntimeError {};    // x % 0
class OverflowError : public RuntimeError {};        // Arithmetic overflow
class UnderflowError : public RuntimeError {};       // Arithmetic underflow
class NaNError : public RuntimeError {};             // Invalid floating-point op
class InfinityError : public RuntimeError {};        // Infinite result

// Forward declare type system exceptions
class TypeError : public RuntimeError {};            // General type issues
class CastError : public TypeError {};               // Failed type cast
class NullReferenceError : public TypeError {};      // Null access
class GenericInstantiationError : public TypeError {}; // Bad template instantiation

// Forward declare text/encoding exceptions
class EncodingError : public RuntimeError {};        // Invalid Unicode
class DecodingError : public EncodingError {};       // Bad UTF-8/16 conversion
class StringIndexError : public RuntimeError {};     // Out-of-bounds access
class RegexError : public RuntimeError {};           // Invalid regex pattern

// Forward declare container exceptions
class IndexError : public RuntimeError {};           // List/array out of bounds
class KeyError : public RuntimeError {};             // Missing map key
class CapacityError : public RuntimeError {};        // Container full
class EmptyContainerError : public RuntimeError {};  // pop() on empty

// Forward declare memory/resource exceptions
class MemoryError : public RuntimeError {};          // Allocation failed
class StackOverflowError : public RuntimeError {};   // Call stack exhausted
class HeapOverflowError : public RuntimeError {};    // Dynamic memory exhausted
class ResourceError : public RuntimeError {};        // Files, sockets, etc.

// Forward declare io exceptions
class IOError : public RuntimeError {};              // General I/O failure
class FileNotFoundError : public IOError {};         // Missing file
class PermissionError : public IOError {};           // Access denied
class EOFError : public IOError {};                  // Unexpected end of file

// Forward declare special cases
class NotImplementedError : public LogicError {};    // Unimplemented feature
class AssertionError : public LogicError {};         // Assertion failed
class SyntaxError : public LogicError {};            // Code parsing errors (compile-time)

// Forward declare container templates
template <typename T>
class EspressoList;

class EspressoCollection;

template <typename Key, typename Value>
class EspressoMap;

