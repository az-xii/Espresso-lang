#pragma once
#include <cstdint>
#include <type_traits>
#include <limits>
#include <stdexcept>
#include <iostream>
#include <string>
#include <utility>
#include <cmath>
#include "./forward_decl.hpp"

// ============== INTEGER TYPE CLASS ==============

template<typename T>
class espresso_integer {
    static_assert(std::is_integral_v<T>, "espresso_integer only works with integral types");
    
    T value;

public:
    // ============== CONSTRUCTORS ==============
    constexpr espresso_integer() noexcept : value(0) {}
    constexpr explicit espresso_integer(T v) noexcept : value(v) {}
    
    // ============== TYPE CONVERSIONS ==============
    constexpr explicit operator T() const noexcept { return value; }
    constexpr explicit operator EspressoBool() const noexcept { return value != 0; }
    
    // ============== ARITHMETIC OPERATORS ==============
    constexpr espresso_integer operator+() const noexcept { return *this; }
    constexpr espresso_integer operator-() const noexcept { return -value; }
    
    constexpr espresso_integer operator+(espresso_integer other) const noexcept {
        return value + other.value;
    }
    
    constexpr espresso_integer operator-(espresso_integer other) const noexcept {
        return value - other.value;
    }
    
    constexpr espresso_integer operator*(espresso_integer other) const noexcept {
        return value * other.value;
    }
    
    constexpr espresso_integer operator/(espresso_integer other) const {
        if (other.value == 0) throw std::domain_error("Division by zero");
        return value / other.value;
    }
    
    constexpr espresso_integer operator%(espresso_integer other) const {
        if (other.value == 0) throw std::domain_error("Modulo by zero");
        return value % other.value;
    }
    
    // ============== BITWISE OPERATORS ==============
    constexpr espresso_integer operator~() const noexcept { return ~value; }
    
    constexpr espresso_integer operator&(espresso_integer other) const noexcept {
        return value & other.value;
    }
    
    constexpr espresso_integer operator|(espresso_integer other) const noexcept {
        return value | other.value;
    }
    
    constexpr espresso_integer operator^(espresso_integer other) const noexcept {
        return value ^ other.value;
    }
    
    constexpr espresso_integer operator<<(espresso_integer other) const {
        if (other.value < 0 || other.value >= sizeof(T)*8) {
            throw std::out_of_range("Invalid shift amount");
        }
        return value << other.value;
    }
    
    constexpr espresso_integer operator>>(espresso_integer other) const {
        if (other.value < 0 || other.value >= sizeof(T)*8) {
            throw std::out_of_range("Invalid shift amount");
        }
        return value >> other.value;
    }
    
    // ============== COMPOUND ASSIGNMENT ==============
    constexpr espresso_integer& operator+=(espresso_integer other) noexcept {
        value += other.value;
        return *this;
    }
    
    constexpr espresso_integer& operator-=(espresso_integer other) noexcept {
        value -= other.value;
        return *this;
    }
    
    constexpr espresso_integer& operator*=(espresso_integer other) noexcept {
        value *= other.value;
        return *this;
    }
    
    constexpr espresso_integer& operator/=(espresso_integer other) {
        *this = *this / other;
        return *this;
    }
    
    constexpr espresso_integer& operator%=(espresso_integer other) {
        *this = *this % other;
        return *this;
    }
    
    constexpr espresso_integer& operator&=(espresso_integer other) noexcept {
        value &= other.value;
        return *this;
    }
    
    constexpr espresso_integer& operator|=(espresso_integer other) noexcept {
        value |= other.value;
        return *this;
    }
    
    constexpr espresso_integer& operator^=(espresso_integer other) noexcept {
        value ^= other.value;
        return *this;
    }
    
    constexpr espresso_integer& operator<<=(espresso_integer other) {
        *this = *this << other;
        return *this;
    }
    
    constexpr espresso_integer& operator>>=(espresso_integer other) {
        *this = *this >> other;
        return *this;
    }
    
    // ============== INCREMENT/DECREMENT ==============
    constexpr espresso_integer& operator++() noexcept {
        ++value;
        return *this;
    }
    
    constexpr espresso_integer operator++(int) noexcept {
        auto tmp = *this;
        ++value;
        return tmp;
    }
    
    constexpr espresso_integer& operator--() noexcept {
        --value;
        return *this;
    }
    
    constexpr espresso_integer operator--(int) noexcept {
        auto tmp = *this;
        --value;
        return tmp;
    }
    
    // ============== COMPARISON OPERATORS ==============
    constexpr EspressoBool operator==(espresso_integer other) const noexcept {
        return value == other.value;
    }
    
    constexpr EspressoBool operator!=(espresso_integer other) const noexcept {
        return value != other.value;
    }
    
    constexpr EspressoBool operator<(espresso_integer other) const noexcept {
        return value < other.value;
    }
    
    constexpr EspressoBool operator<=(espresso_integer other) const noexcept {
        return value <= other.value;
    }
    
    constexpr EspressoBool operator>(espresso_integer other) const noexcept {
        return value > other.value;
    }
    
    constexpr EspressoBool operator>=(espresso_integer other) const noexcept {
        return value >= other.value;
    }
    
    // ============== UTILITY METHODS ==============
    constexpr T underlying() const noexcept { return value; }
    
    std::string to_string() const {
        return std::to_string(value);
    }
    
    constexpr espresso_integer abs() const noexcept {
        return value < 0 ? -value : value;
    }
    
    template<typename U>
    constexpr espresso_integer<U> as() const {
        if constexpr (std::is_signed_v<T> && std::is_unsigned_v<U>) {
            if (value < 0) throw std::range_error("Negative to unsigned conversion");
        }
        if (value < std::numeric_limits<U>::min() || 
            value > std::numeric_limits<U>::max()) {
            throw std::overflow_error("Integer conversion overflow");
        }
        return static_cast<U>(value);
    }
    
    // ============== FRIEND OPERATORS ==============
    friend std::ostream& operator<<(std::ostream& os, espresso_integer n) {
        return os << n.value;
    }
    
    friend std::istream& operator>>(std::istream& is, espresso_integer& n) {
        T tmp;
        is >> tmp;
        n.value = tmp;
        return is;
    }
};

// ============== TYPE ALIASES ==============
using EspressoByte = espresso_integer<int8_t>;
using EspressoShort = espresso_integer<int16_t>;
using EspressoInt = espresso_integer<int32_t>;
using EspressoLong = espresso_integer<int64_t>;
using EspressoLongLong = espresso_integer<__int128>;

using EspressoUByte = espresso_integer<uint8_t>;
using EspressoUShort = espresso_integer<uint16_t>;
using EspressoUInt = espresso_integer<uint32_t>;
using EspressoULong = espresso_integer<uint64_t>;
using EspressoULongLong = espresso_integer<unsigned __int128>;

// ============== LITERAL OPERATORS ==============
constexpr EspressoByte operator""i8(unsigned long long v) {
    return EspressoByte{static_cast<int8_t>(v)};
}
constexpr EspressoShort operator""i16(unsigned long long v) {
    return EspressoShort{static_cast<int16_t>(v)};
}
constexpr EspressoInt operator""i32(unsigned long long v) {
    return EspressoInt{static_cast<int32_t>(v)};
}
constexpr EspressoLong operator""i64(unsigned long long v) {
    return EspressoLong{static_cast<int64_t>(v)};
}
constexpr EspressoLongLong operator""i128(unsigned long long v) {
    return EspressoLongLong{static_cast<__int128>(v)};
}

constexpr EspressoUByte operator""u8(unsigned long long v) {
    return EspressoUByte{static_cast<uint8_t>(v)};
}
constexpr EspressoUShort operator""u16(unsigned long long v) {
    return EspressoUShort{static_cast<uint16_t>(v)};
}
constexpr EspressoUInt operator""u32(unsigned long long v) {
    return EspressoUInt{static_cast<uint32_t>(v)};
}
constexpr EspressoULong operator""u64(unsigned long long v) {
    return EspressoULong{static_cast<uint64_t>(v)};
}
constexpr EspressoULongLong operator""u128(unsigned long long v) {
    return EspressoULongLong{static_cast<unsigned __int128>(v)};
}


// ============== FLOATING POINT TYPE CLASS ==============

template<typename T>
class espresso_float {
    static_assert(std::is_floating_point_v<T>, 
                 "espresso_float only works with floating-point types");
    
    T value;

public:
    // ============== CONSTRUCTORS ==============
    constexpr espresso_float() noexcept : value(0) {}
    constexpr explicit espresso_float(T v) noexcept : value(v) {}
    
    // ============== TYPE CONVERSIONS ==============
    constexpr explicit operator T() const noexcept { return value; }
    constexpr explicit operator EspressoBool() const noexcept { return value != 0; }
    
    // ============== ARITHMETIC OPERATORS ==============
    constexpr espresso_float operator+() const noexcept { return *this; }
    constexpr espresso_float operator-() const noexcept { return -value; }
    
    constexpr espresso_float operator+(espresso_float other) const noexcept {
        return value + other.value;
    }
    
    constexpr espresso_float operator-(espresso_float other) const noexcept {
        return value - other.value;
    }
    
    constexpr espresso_float operator*(espresso_float other) const noexcept {
        return value * other.value;
    }
    
    constexpr espresso_float operator/(espresso_float other) const {
        if (other.value == 0) throw std::domain_error("Division by zero");
        return value / other.value;
    }
    
    // ============== COMPOUND ASSIGNMENT ==============
    constexpr espresso_float& operator+=(espresso_float other) noexcept {
        value += other.value;
        return *this;
    }
    
    constexpr espresso_float& operator-=(espresso_float other) noexcept {
        value -= other.value;
        return *this;
    }
    
    constexpr espresso_float& operator*=(espresso_float other) noexcept {
        value *= other.value;
        return *this;
    }
    
    constexpr espresso_float& operator/=(espresso_float other) {
        *this = *this / other;
        return *this;
    }
    
    // ============== COMPARISON OPERATORS ==============
    constexpr EspressoBool operator==(espresso_float other) const noexcept {
        return value == other.value;
    }
    
    constexpr EspressoBool operator!=(espresso_float other) const noexcept {
        return value != other.value;
    }
    
    constexpr EspressoBool operator<(espresso_float other) const noexcept {
        return value < other.value;
    }
    
    constexpr EspressoBool operator<=(espresso_float other) const noexcept {
        return value <= other.value;
    }
    
    constexpr EspressoBool operator>(espresso_float other) const noexcept {
        return value > other.value;
    }
    
    constexpr EspressoBool operator>=(espresso_float other) const noexcept {
        return value >= other.value;
    }
    
    // ============== MATH FUNCTIONS ==============
    constexpr espresso_float abs() const noexcept {
        return std::abs(value);
    }
    
    espresso_float sqrt() const {
        if (value < 0) throw std::domain_error("Square root of negative number");
        return std::sqrt(value);
    }
    
    espresso_float sin() const noexcept { return std::sin(value); }
    espresso_float cos() const noexcept { return std::cos(value); }
    espresso_float tan() const noexcept { return std::tan(value); }
    
    espresso_float log() const {
        if (value <= 0) throw std::domain_error("Log of non-positive number");
        return std::log(value);
    }
    
    espresso_float exp() const noexcept { return std::exp(value); }
    
    // ============== UTILITY METHODS ==============
    constexpr T underlying() const noexcept { return value; }
    
    std::string to_string() const {
        return std::to_string(value);
    }
    
    EspressoBool is_nan() const noexcept { return std::isnan(value); }
    EspressoBool is_inf() const noexcept { return std::isinf(value); }
    EspressoBool is_finite() const noexcept { return std::isfinite(value); }
    
    // ============== FRIEND OPERATORS ==============
    friend std::ostream& operator<<(std::ostream& os, espresso_float n) {
        return os << n.value;
    }
    
    friend std::istream& operator>>(std::istream& is, espresso_float& n) {
        T tmp;
        is >> tmp;
        n.value = tmp;
        return is;
    }
};
// ====================================================

// ============== TYPE ALIASES ==============
using EspressoFloat = espresso_float<float>;
using EspressoDouble = espresso_float<double>;
using EspressoDecimal = espresso_float<long double>;

// ============== LITERAL OPERATORS ==============
constexpr EspressoFloat operator""f32(long double v) {
    return EspressoFloat{static_cast<float>(v)};
}
constexpr EspressoDouble operator""f64(long double v) {
    return EspressoDouble{static_cast<double>(v)};
}
constexpr EspressoDecimal operator""f128(long double v) {
    return EspressoDecimal{static_cast<long double>(v)};
}


// ============== FIXED POINT TYPE CLASS ==============

template<typename BaseType, size_t FractionalBits>
class espresso_fixed {
    static_assert(std::is_integral_v<BaseType>, 
                 "BaseType must be an integral type");
    static_assert(FractionalBits < sizeof(BaseType)*8,
                 "Too many fractional bits");
    
    BaseType value;
    static constexpr BaseType scale = BaseType(1) << FractionalBits;

public:
    // ============== CONSTRUCTORS ==============
    constexpr espresso_fixed() noexcept : value(0) {}
    
    explicit constexpr espresso_fixed(BaseType v) noexcept : value(v) {}
    
    template<typename T>
    explicit constexpr espresso_fixed(T v) noexcept : 
        value(static_cast<BaseType>(v * scale)) {}
    
    // ============== ARITHMETIC OPERATORS ==============
    constexpr espresso_fixed operator+() const noexcept { return *this; }
    constexpr espresso_fixed operator-() const noexcept { return -value; }
    
    constexpr espresso_fixed operator+(espresso_fixed other) const noexcept {
        return espresso_fixed(value + other.value);
    }
    
    constexpr espresso_fixed operator-(espresso_fixed other) const noexcept {
        return espresso_fixed(value - other.value);
    }
    
    constexpr espresso_fixed operator*(espresso_fixed other) const noexcept {
        return espresso_fixed((value * other.value) >> FractionalBits);
    }
    
    constexpr espresso_fixed operator/(espresso_fixed other) const {
        if (other.value == 0) throw std::domain_error("Division by zero");
        return espresso_fixed((value << FractionalBits) / other.value);
    }
    
    // ============== COMPOUND ASSIGNMENT ==============
    constexpr espresso_fixed& operator+=(espresso_fixed other) noexcept {
        value += other.value;
        return *this;
    }
    
    constexpr espresso_fixed& operator-=(espresso_fixed other) noexcept {
        value -= other.value;
        return *this;
    }
    
    constexpr espresso_fixed& operator*=(espresso_fixed other) noexcept {
        *this = *this * other;
        return *this;
    }
    
    constexpr espresso_fixed& operator/=(espresso_fixed other) {
        *this = *this / other;
        return *this;
    }
    
    // ============== UTILITY METHODS ==============
    constexpr BaseType raw() const noexcept { return value; }
    constexpr double to_double() const noexcept { 
        return static_cast<double>(value) / scale; 
    }
    
    std::string to_string() const {
        return std::to_string(to_double());
    }
    
    // Rounding operations
    constexpr espresso_fixed round() const noexcept {
        return espresso_fixed((value + (scale/2)) & ~(scale-1));
    }
    
    // ============== FRIEND OPERATORS ==============
    friend std::ostream& operator<<(std::ostream& os, espresso_fixed n) {
        return os << n.to_double();
    }
};

// Common fixed-point types
using EspressoFixed16_16 = espresso_fixed<int32_t, 16>;
using EspressoFixed32_32 = espresso_fixed<int64_t, 32>;
using EspressoUFixed16_16 = espresso_fixed<uint32_t, 16>;

// Literal operator
constexpr EspressoFixed16_16 operator""fx1616(long double v) {
    return EspressoFixed16_16{v};
}
constexpr EspressoFixed32_32 operator""fx3232(long double v) {
    return EspressoFixed32_32{v};
}
constexpr EspressoUFixed16_16 operator""ufx1616(long double v) {
    return EspressoUFixed16_16{v};
}


// ============== SPECIAL TYPE CLASSES ==============

using EspressoBool = bool;
using EspressoVoid = void;
using EspressoNullptr = std::nullptr_t;

