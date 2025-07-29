#pragma once
#include <stdexcept>
#include <string>

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
