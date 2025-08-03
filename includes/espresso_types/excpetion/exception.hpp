#pragma once
#include <stdexcept>
#include <string>
#include "../forward_decl.hpp"

// ============== EXCEPTION CLASSES==============

class Error : public std::exception {
    EspressoString message;
public:
    explicit Error(EspressoString msg) : message(std::move(msg)) {}
    const char* what() const noexcept override { return message.utf8().c_str(); }
};
class RuntimeError : public Error {
public:
    using Error::Error;
};
class LogicError : public Error {
public:
    using Error::Error;
};


// ============== ARITHMETIC EXCEPTION CLASSES ==============

class DivisionByZeroError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};
class ModuloByZeroError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};  
class OverflowError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};      
class UnderflowError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};     
class NaNError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};           
class InfinityError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};


// ============== TYPE EXCEPTION CLASSES ==============

class TypeError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};            
class CastError : public TypeError {
    public:
    using TypeError::TypeError;
};               
class NullReferenceError : public TypeError {
    public:
    using TypeError::TypeError;
};      
class GenericInstantiationError : public TypeError {
    public:
    using TypeError::TypeError;
};


// ============== TEXT/ENCODING EXCEPTION CLASSES ==============

class EncodingError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};
class DecodingError : public EncodingError {
    public:
    using RuntimeError::RuntimeError;
};
class StringIndexError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};
class RegexError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};


// ============== CONTAINER EXCEPTION CLASSES ==============

class IndexError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};
class KeyError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};
class CapacityError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};
class EmptyContainerError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};


// ============== IO EXCEPTION CLASSES ==============
class IOError : public RuntimeError {
    public:
    using RuntimeError::RuntimeError;
};
class FileNotFoundError : public IOError {
    public:
    using IOError::IOError;
};
class PermissionError : public IOError {
    public:
    using IOError::IOError;
};
class EOFError : public IOError {
    public:
    using IOError::IOError;
};
