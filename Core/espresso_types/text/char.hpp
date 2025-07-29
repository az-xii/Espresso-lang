#pragma once
#include "../forward_decl.hpp"
#include <cstdint>            // For char32_t

class EspressoChar {
    char32_t value;
    
public:
    // Constructor
    constexpr EspressoChar(char32_t v = 0) : value(v) {}

    // Character operations
    constexpr bool is_digit() const noexcept { 
        return value >= U'0' && value <= U'9'; 
    }
    
    // Conversion to numeric
    explicit operator EspressoInt() const {
        if (!is_digit()) {
            throw EncodingError("Non-digit character conversion attempted");
        }
        return EspressoInt(static_cast<int32_t>(value - U'0'));
    }

    // Value access
    constexpr char32_t code_point() const noexcept { return value; }
};