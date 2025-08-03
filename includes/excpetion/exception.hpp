#pragma once
#include <stdexcept>
#include "../forward_decl.hpp"
class Error : public std::exception {
    EspressoString message;
public:
    explicit Error(EspressoString msg) : message(std::move(msg)) {}
    const char* what() const noexcept override { return message.utf8().c_str(); }
};



// ================== CATEGORY BASE CLASSES ==================
class LogicError : public Error {
    using Error::Error;
};

class RuntimeError : public Error {
    using Error::Error;
};

// ================== ARITHMETIC ERRORS ==================
class DivisionByZeroError : public RuntimeError {
public:
    DivisionByZeroError()
        : RuntimeError("Division by zero") {}
};

class ModuloByZeroError : public RuntimeError {
public:
    ModuloByZeroError()
        : RuntimeError("Modulo by zero") {}
};

class OverflowError : public RuntimeError {
public:
    OverflowError()
        : RuntimeError("Arithmetic overflow") {}
};

// ================== TYPE ERRORS ==================
class TypeError : public RuntimeError {
public:
    explicit TypeError(EspressoString details)
        : RuntimeError("Type error: " + details) {}
};

class CastError : public TypeError {
public:
    CastError(EspressoString from, EspressoString to)
        : TypeError("Cannot cast from " + from + " to " + to) {}
};

// ================== TEXT/ENCODING ERRORS ==================
class EncodingError : public RuntimeError {
public:
    explicit EncodingError(EspressoString details)
        : RuntimeError("Encoding error: " + details) {}
};

class StringIndexError : public RuntimeError {
public:
    StringIndexError(size_t index, size_t length)
        : RuntimeError("Index " + std::to_string(index) + 
                      " out of bounds for length " + std::to_string(length)) {}
};

// ================== CONTAINER ERRORS ==================
class IndexError : public RuntimeError {
public:
    IndexError(size_t index, size_t size)
        : RuntimeError("Container index " + std::to_string(index) +
                      " out of range (size " + std::to_string(size) + ")") {}
};

class KeyError : public RuntimeError {
public:
    explicit KeyError(EspressoString key)
        : RuntimeError("Key not found: " + key) {}
};

// ================== SYSTEM ERRORS ==================
class IOError : public RuntimeError {
public:
    explicit IOError(EspressoString path)
        : RuntimeError("I/O error with: " + path) {}
};

class FileNotFoundError : public IOError {
public:
    explicit FileNotFoundError(EspressoString path)
        : IOError("File not found: " + path) {}
};

// ================== SPECIAL CASES ==================
class NotImplementedError : public LogicError {
public:
    NotImplementedError()
        : LogicError("Feature not implemented") {}
};

class AssertionError : public LogicError {
public:
    explicit AssertionError(EspressoString condition)
        : LogicError("Assertion failed: " + condition) {}
};