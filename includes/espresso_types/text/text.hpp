#pragma once
#include "../forward_decl.hpp"
#include <cstdint>            // For char32_t
#include <iostream>
#include <vector>

struct EspressoChar {
    char32_t value; // one Unicode code point

    EspressoChar() : value(0) {}
    EspressoChar(char32_t v) : value(v) {}

    // Conversion from char literal
    EspressoChar(char c) : value(static_cast<char32_t>(c)) {}

    constexpr EspressoChar(char32_t v = 0) : value(v) {}

    // Access underlying code point
    constexpr char32_t code_point() const noexcept { return value; }

    // Digit check
    constexpr bool is_digit() const noexcept {
        return value >= U'0' && value <= U'9';
    }

    // Alpha check
    constexpr bool is_alpha() const noexcept {
        return (value >= U'a' && value <= U'z') || (value >= U'A' && value <= U'Z');
    }

    // Alphanumeric
    constexpr bool is_alnum() const noexcept {
        return is_alpha() || is_digit();
    }

    // Whitespace
    constexpr bool is_whitespace() const noexcept {
        return value == U' ' || value == U'\t' || value == U'\n' || value == U'\r';
    }

    // Explicit numeric conversion for digits only
    explicit operator int() const {
        if (!is_digit()) {
            throw EncodingError("Non-digit character conversion attempted");
        }
        return static_cast<int>(value - U'0');
    }

    // Equality
    constexpr bool operator==(const EspressoChar& other) const noexcept {
        return value == other.value;
    }

    constexpr bool operator!=(const EspressoChar& other) const noexcept {
        return !(*this == other);
    }

    // Ordering (optional but handy)
    constexpr bool operator<(const EspressoChar& other) const noexcept {
        return value < other.value;
    }

    constexpr bool operator<=(const EspressoChar& other) const noexcept {
        return value <= other.value;
    }

    constexpr bool operator>(const EspressoChar& other) const noexcept {
        return value > other.value;
    }

    constexpr bool operator>=(const EspressoChar& other) const noexcept {
        return value >= other.value;
    }

    friend std::ostream& operator<<(std::ostream& os, const EspressoChar& c) {
        return os << static_cast<char>(c.value); // You can change this to UTF-8 conversion
    }
};

class EspressoString {
    std::vector<EspressoChar> data;

public:
    EspressoString() = default;

    EspressoString(const char* cstr) {
        while (*cstr) {
            data.push_back(EspressoChar(*cstr++));
        }
    }

    size_t length() const {
        return data.size();
    }

    EspressoChar& operator[](size_t i) {
        return data[i];
    }

    const EspressoChar& operator[](size_t i) const {
        return data[i];
    }

    EspressoString operator+(const EspressoString& other) const {
        EspressoString result = *this;
        result.data.insert(result.data.end(), other.data.begin(), other.data.end());
        return result;
    }

    bool operator==(const EspressoString& other) const {
        return data == other.data;
    }

    friend std::ostream& operator<<(std::ostream& os, const EspressoString& str) {
        for (auto c : str.data) {
            os << c;
        }
        return os;
    }
};
