#pragma once
#include "../core/runtime.hpp"
#include <random>
#include <cmath>
#include <algorithm>
#include <numeric>

#ifndef ESP_MATH_HPP
#define ESP_MATH_HPP

namespace math {
    // ===== CONSTANTS =====
    constexpr double PI = 3.14159265358979323846;
    constexpr double E  = 2.71828182845904523536;
    constexpr double GOLDEN_RATIO = 1.618033988749895;
    constexpr double SQRT2 = 1.41421356237309504880;
    constexpr double SQRT1_2 = 0.70710678118654752440;
    constexpr double LN2 = 0.69314718055994530942;
    constexpr double LN10 = 2.30258509299404568402;
    constexpr double GRAVITY = 9.80665; // Standard gravity (m/s²)
    constexpr double SPEED_OF_LIGHT = 299792458; // in m/s
    constexpr double PLANCK_CONSTANT = 6.62607015e-34; // in Js
    constexpr double AVOGADRO_NUMBER = 6.02214076e23; // in mol⁻¹
    const double NaNValue = std::numeric_limits<double>::quiet_NaN();
    const double INF = std::numeric_limits<double>::infinity();
    const double NEG_INF = -std::numeric_limits<double>::infinity();

    // ===== BASIC FUNCTIONS =====
    template<typename T>
    T Abs(T value) {
        return std::abs(value);
    }

    template<typename T>
    T Power(T base, T exponent) {
        return std::pow(base, exponent);
    }

    template<typename T>
    T Sqrt(T value) {
        if (value < 0) throw LogicError("Square root of negative number");
        return std::sqrt(value);
    }

    template<typename T>
    T Exp(T value) {
        return std::exp(value);
    }

    template<typename T>
    T Log(T value) {
        if (value <= 0) throw LogicError("Logarithm of non-positive number");
        return std::log(value);
    }

    template<typename T>
    T Log10(T value) {
        if (value <= 0) throw LogicError("Log10 of non-positive number");
        return std::log10(value);
    }

    // ===== TRIGONOMETRY =====
    template<typename T>
    T Sin(T radians) {
        return std::sin(radians);
    }

    template<typename T>
    T Cos(T radians) {
        return std::cos(radians);
    }

    template<typename T>
    T Tan(T radians) {
        return std::tan(radians);
    }

    template<typename T>
    T ASin(T value) {
        if (value < -1 || value > 1) throw LogicError("Invalid input for arcsin");
        return std::asin(value);
    }

    template<typename T>
    T ACos(T value) {
        if (value < -1 || value > 1) throw LogicError("Invalid input for arccos");
        return std::acos(value);
    }

    template<typename T>
    T ATan(T value) {
        return std::atan(value);
    }

    template<typename T>
    T ATan2(T y, T x) {
        return std::atan2(y, x);
    }

    template<typename T>
    T DegreesToRadians(T degrees) {
        return degrees * (PI / 180.0);
    }

    template<typename T>
    T RadiansToDegrees(T radians) {
        return radians * (180.0 / PI);
    }

    // ===== RANGE FUNCTION =====
    template<typename T>
    ListWrapper<T> Range(T start, T end, T step = 1) {
        if (step == 0) throw LogicError("Step cannot be zero in Range()");
        ListWrapper<T> result;
        if ((step > 0 && start >= end) || (step < 0 && start <= end)) {
            return result; // Empty list
        }
        for (T value = start; (step > 0) ? (value < end) : (value > end); value += step) {
            result.Append(value);
        }
        return result;
    }

    // ===== STATISTICS =====
    template<typename T>
    T Mode(const ListWrapper<T>& data) {
        if (data.Empty()) throw ValueError("Cannot compute mode of an empty list");
        std::map<T, size_t> frequency;
        for (const auto& item : data) {
            frequency[item]++;
        }
        using PairType = std::pair<T, size_t>;
        auto cmp = [](const PairType& a, const PairType& b) {
            return a.second < b.second; // Compare by frequency
        };
        auto max_elem = std::max_element(frequency.begin(), frequency.end(), cmp);
        return max_elem->first;
    }

    template<typename T>
    double Median(ListWrapper<T> data) {
        if (data.Empty()) throw ValueError("Cannot compute median of an empty list");
        std::sort(data.begin(), data.end());
        size_t n = data.Size();
        if (n % 2 == 1) {
            return static_cast<double>(data[n / 2]);
        } else {
            return (static_cast<double>(data[n / 2 - 1]) + static_cast<double>(data[n / 2])) / 2.0;
        }
    }

    template<typename T>
    double Mean(const ListWrapper<T>& data) {
        if (data.Empty()) throw ValueError("Cannot compute mean of an empty list");
        double sum = 0.0;
        for (const auto& item : data) {
            sum += static_cast<double>(item);
        }
        return sum / data.Size();
    }

    template<typename T>
    double Variance(const ListWrapper<T>& data, bool sample = true) {
        if (data.Empty()) throw ValueError("Cannot compute variance of an empty list");
        double mean = Mean(data);
        double sum_sq_diff = 0.0;
        for (const auto& item : data) {
            double diff = static_cast<double>(item) - mean;
            sum_sq_diff += diff * diff;
        }
        return sum_sq_diff / (data.Size() - (sample ? 1 : 0));
    }

    template<typename T>
    double StandardDeviation(const ListWrapper<T>& data, bool sample = true) {
        return Sqrt(Variance(data, sample));
    }

    // ===== RANDOM DISTRIBUTIONS =====
    template<typename T>
    T Uniform(T a, T b) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        if constexpr (std::is_integral_v<T>) {
            std::uniform_int_distribution<T> dist(a, b);
            return dist(gen);
        } else {
            std::uniform_real_distribution<T> dist(a, b);
            return dist(gen);
        }
    }

    template<typename T>
    T Normal(T mean, T stddev) {
        static std::random_device rd;
        static std::mt19937 gen(rd());
        std::normal_distribution<T> dist(mean, stddev);
        return dist(gen);
    }

    // ===== VECTOR/MATRIX MATH (For your physics simulation!) =====
    template<typename T>
    T DotProduct(const ListWrapper<T>& a, const ListWrapper<T>& b) {
        if (a.Size() != b.Size()) throw ValueError("Vectors must have same size for dot product");
        T result = 0;
        for (size_t i = 0; i < a.Size(); ++i) {
            result += a[i] * b[i];
        }
        return result;
    }

    template<typename T>
    T Magnitude(const ListWrapper<T>& vec) {
        return Sqrt(DotProduct(vec, vec));
    }

    template<typename T>
    ListWrapper<T> Normalize(const ListWrapper<T>& vec) {
        T mag = Magnitude(vec);
        if (mag == 0) throw LogicError("Cannot normalize zero vector");
        ListWrapper<T> result;
        for (const auto& component : vec) {
            result.Append(component / mag);
        }
        return result;
    }

    // ===== PHYSICS HELPERS =====
    template<typename T>
    T KineticEnergy(T mass, T velocity) {
        return 0.5 * mass * velocity * velocity;
    }

    template<typename T>
    T PotentialEnergy(T mass, T height, T gravity = GRAVITY) {
        return mass * gravity * height;
    }

    // Clamp value between min and max
    template<typename T>
    T Clamp(T value, T min_val, T max_val) {
        return std::clamp(value, min_val, max_val);
    }

    // Linear interpolation
    template<typename T>
    T Lerp(T a, T b, T t) {
        return a + t * (b - a);
    }

    // ===== COMPARISON FUNCTIONS =====
    template<typename T>
    bool ApproximatelyEqual(T a, T b, T tolerance = 1e-6) {
        return Abs(a - b) <= tolerance;
    }

} // namespace math

#endif // ESP_MATH_HPP
