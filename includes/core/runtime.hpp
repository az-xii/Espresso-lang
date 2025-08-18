#ifndef RUNTIME_HPP
#define RUNTIME_HPP

#include <iostream>
#include <string>
#include <memory>
#include <typeinfo>
#include <type_traits>
#include <limits>
#include <exception>
#include <cstdint>
#include <vector>
#include <functional>
// ===== FORWARD DECLARATIONS =====
class Object;
template <typename T> class Wrapper;
class StringWrapper;

template <typename Derived, typename T> class NumericWrapper;

// Numeric type forward declarations
class ByteWrapper;
class ShortWrapper;
class IntWrapper;
class LongWrapper;

class UByteWrapper;
class UShortWrapper;
class UIntWrapper;
class ULongWrapper;

class FloatWrapper;
class DoubleWrapper;
class Fixed16_16;
class Fixed32_32;
class UFixed16_16;
class UFixed32_32;

// ===== EXCEPTION HIERARCHY =====
class Error : public std::exception {
    std::string message;
public:
    explicit Error(const std::string& msg);
    const char* what() const noexcept override;
};

class RuntimeError : public Error { public: using Error::Error; };
class LogicError   : public Error { public: using Error::Error; };

// ===== Arithmetic Exceptions =====
class DivisionByZeroError : public RuntimeError { public: using RuntimeError::RuntimeError; };
class ModuloByZeroError   : public RuntimeError { public: using RuntimeError::RuntimeError; };
class OverflowError       : public RuntimeError { public: using RuntimeError::RuntimeError; };
class UnderflowError      : public RuntimeError { public: using RuntimeError::RuntimeError; };
class NaNError            : public RuntimeError { public: using RuntimeError::RuntimeError; };
class InfinityError       : public RuntimeError { public: using RuntimeError::RuntimeError; };

// ===== Type Exceptions =====
class TypeError                  : public RuntimeError { public: using RuntimeError::RuntimeError; };
class CastingError               : public TypeError     { public: using TypeError::TypeError; };
class NullReferenceError         : public TypeError     { public: using TypeError::TypeError; };
class GenericInstantiationError  : public TypeError     { public: using TypeError::TypeError; };

// ===== Text/Encoding Exceptions =====
class EncodingError : public RuntimeError { public: using RuntimeError::RuntimeError; };
class DecodingError : public EncodingError { public: using EncodingError::EncodingError; };
class StringIndexError : public RuntimeError { public: using RuntimeError::RuntimeError; };
class RegexError : public RuntimeError { public: using RuntimeError::RuntimeError; };

// ===== Container Exceptions =====
class IndexError         : public RuntimeError { public: using RuntimeError::RuntimeError; };
class KeyError           : public RuntimeError { public: using RuntimeError::RuntimeError; };
class CapacityError      : public RuntimeError { public: using RuntimeError::RuntimeError; };
class EmptyContainerError: public RuntimeError { public: using RuntimeError::RuntimeError; };

// ===== I/O Exceptions =====
class IOError            : public RuntimeError { public: using RuntimeError::RuntimeError; };
class FileNotFoundError  : public IOError { public: using IOError::IOError; };
class PermissionError    : public IOError { public: using IOError::IOError; };
class EOFError           : public IOError { public: using IOError::IOError; };

// ==== Composite Types ====
template<typename T>
class ListWrapper;

class CollectionWrapper;

template<typename... Ts>
class TupleWrapper;

template<typename K, typename V>
class MapWrapper;

template<typename T>
class SetWrapper;

template<typename... Ts>
class UnionWrapper;

template<typename Ret, typename... Args>
class LambdaWrapper;

// ===== BASE CLASSES =====
class Object {
public:
    virtual ~Object() = default;
    virtual const std::type_info& type() const noexcept;
};

template <typename T>
class Wrapper : public Object {
public:
    const std::type_info& type() const noexcept override;
};

// ===== UTILITY FUNCTIONS =====
template <typename T>
bool isinstance(const std::shared_ptr<Object>& obj);

template <typename T, typename U>
T cast(const U& obj);

template <typename T>
const char* type_name();

// ===== STRING CLASS =====
class StringWrapper : public Wrapper<StringWrapper> {
private:
    std::string data;

public:
    // Type aliases
    using iterator = std::string::iterator;
    using const_iterator = std::string::const_iterator;

    // Constructors
    StringWrapper();
    StringWrapper(const std::string& s);
    StringWrapper(std::string&& s) noexcept;
    StringWrapper(const char* s);

    // Core accessors
    const std::string& str() const noexcept;
    size_t length_bytes() const noexcept;
    size_t length() const;  // UTF-8 codepoint count
    bool empty() const noexcept;

    // UTF-8 operations
    char32_t at(size_t index) const;
    std::string utf8() const noexcept;

    // Iterators (byte-level)
    iterator begin();
    iterator end();
    const_iterator begin() const;
    const_iterator end() const;

    // C-style access
    const char* c_str() const noexcept;

    // Validation
    static bool is_valid_utf8(const std::string& s) noexcept;
};

// ===== NUMERIC BASE CLASS =====
template <typename Derived, typename T>
class NumericWrapper : public Wrapper<Derived> {
protected:
    T value{};

public:
    // Constructors
    NumericWrapper() = default;
    explicit NumericWrapper(T v);

    // Access
    T get() const;
    operator T() const;

    // Explicit conversion with overflow checking
    template<typename Target>
    explicit operator Target() const;

    // Arithmetic operators
    Derived operator+(const Derived& other) const;
    Derived operator-(const Derived& other) const;
    Derived operator*(const Derived& other) const;
    Derived operator/(const Derived& other) const;
    Derived operator%(const Derived& other) const;
    Derived operator+() const;
    Derived operator-() const;

    // Compound arithmetic
    Derived& operator+=(const Derived& other);
    Derived& operator-=(const Derived& other);
    Derived& operator*=(const Derived& other);
    Derived& operator/=(const Derived& other);
    Derived& operator%=(const Derived& other);

    // Comparisons
    bool operator==(const Derived& other) const;
    bool operator!=(const Derived& other) const;
    bool operator<(const Derived& other) const;
    bool operator>(const Derived& other) const;
    bool operator<=(const Derived& other) const;
    bool operator>=(const Derived& other) const;

    // Bitwise operations (integral types only)
    template<typename U = T>
    std::enable_if_t<std::is_integral_v<U>, Derived> operator&(const Derived& other) const;

    template<typename U = T>
    std::enable_if_t<std::is_integral_v<U>, Derived> operator|(const Derived& other) const;

    template<typename U = T>
    std::enable_if_t<std::is_integral_v<U>, Derived> operator^(const Derived& other) const;

    template<typename U = T>
    std::enable_if_t<std::is_integral_v<U>, Derived> operator~() const;

    template<typename U = T>
    std::enable_if_t<std::is_integral_v<U>, Derived> operator<<(int shift) const;

    template<typename U = T>
    std::enable_if_t<std::is_integral_v<U>, Derived> operator>>(int shift) const;

    // Assignment
    Derived& operator=(T v);

    // Output
    friend std::ostream& operator<<(std::ostream& os, const Derived& obj) {
        return os << obj.value;
    }
};

// ===== CONCRETE NUMERIC TYPES =====
class ByteWrapper   : public NumericWrapper<ByteWrapper, int8_t> { public: using NumericWrapper::NumericWrapper; };
class ShortWrapper  : public NumericWrapper<ShortWrapper, int16_t> { public: using NumericWrapper::NumericWrapper; };
class IntWrapper    : public NumericWrapper<IntWrapper, int32_t> { public: using NumericWrapper::NumericWrapper; };
class LongWrapper   : public NumericWrapper<LongWrapper, int64_t> { public: using NumericWrapper::NumericWrapper; };

class UByteWrapper  : public NumericWrapper<UByteWrapper, uint8_t> { public: using NumericWrapper::NumericWrapper; };
class UShortWrapper : public NumericWrapper<UShortWrapper, uint16_t> { public: using NumericWrapper::NumericWrapper; };
class UIntWrapper   : public NumericWrapper<UIntWrapper, uint32_t> { public: using NumericWrapper::NumericWrapper; };
class ULongWrapper  : public NumericWrapper<ULongWrapper, uint64_t> { public: using NumericWrapper::NumericWrapper; };

class FloatWrapper  : public NumericWrapper<FloatWrapper, float> { public: using NumericWrapper::NumericWrapper; };
class DoubleWrapper : public NumericWrapper<DoubleWrapper, double> { public: using NumericWrapper::NumericWrapper; };
class Fixed16_16    : public NumericWrapper<Fixed16_16, int32_t> { public: using NumericWrapper::NumericWrapper; }; 
class Fixed32_32    : public NumericWrapper<Fixed32_32, int64_t> { public: using NumericWrapper::NumericWrapper; };
class UFixed16_16   : public NumericWrapper<UFixed16_16, u_int32_t> { public: using NumericWrapper::NumericWrapper; };
class UFixed32_32   : public NumericWrapper<UFixed32_32, u_int64_t> { public: using NumericWrapper::NumericWrapper; };

// ===== TEMPLATE IMPLEMENTATIONS =====
// These need to be in the header since they're templates

template <typename T>
const std::type_info& Wrapper<T>::type() const noexcept {
    return typeid(T);
}

template <typename T>
bool isinstance(const std::shared_ptr<Object>& obj) {
    return std::dynamic_pointer_cast<T>(obj) != nullptr;
}

template <typename T, typename U>
T cast(const U& obj) {
    if constexpr (std::is_convertible_v<U, T>) {
        return static_cast<T>(obj);
    } else {
        throw CastingError("Conversion failed");
    }
}

template <typename T>
const char* type_name() {
    if constexpr (std::is_same_v<T, int>) return "int";
    else if constexpr (std::is_same_v<T, float>) return "float";
    else if constexpr (std::is_same_v<T, double>) return "double";
    else if constexpr (std::is_same_v<T, std::string>) return "string";
    else return typeid(T).name();
}

// NumericWrapper template implementations
template <typename Derived, typename T>
NumericWrapper<Derived, T>::NumericWrapper(T v) : value(v) {}

template <typename Derived, typename T>
T NumericWrapper<Derived, T>::get() const { return value; }

template <typename Derived, typename T>
NumericWrapper<Derived, T>::operator T() const { return value; }

template <typename Derived, typename T>
template<typename Target>
NumericWrapper<Derived, T>::operator Target() const {
    if constexpr (std::is_same_v<T, Target>) {
        return value;
    } else if constexpr (std::is_arithmetic_v<Target>) {
        if (value > std::numeric_limits<Target>::max() ||
            value < std::numeric_limits<Target>::lowest()) {
            throw OverflowError("Numeric conversion overflow");
        }
        return static_cast<Target>(value);
    } else {
        throw CastingError("Invalid numeric conversion");
    }
}

// Arithmetic operators
template <typename Derived, typename T>
Derived NumericWrapper<Derived, T>::operator+(const Derived& other) const { 
    return Derived(value + other.value); 
}

template <typename Derived, typename T>
Derived NumericWrapper<Derived, T>::operator-(const Derived& other) const { 
    return Derived(value - other.value); 
}

template <typename Derived, typename T>
Derived NumericWrapper<Derived, T>::operator*(const Derived& other) const { 
    return Derived(value * other.value); 
}

template <typename Derived, typename T>
Derived NumericWrapper<Derived, T>::operator/(const Derived& other) const { 
    if (other.value == 0) throw DivisionByZeroError("Division by zero");
    return Derived(value / other.value); 
}

template <typename Derived, typename T>
Derived NumericWrapper<Derived, T>::operator%(const Derived& other) const { 
    if (other.value == 0) throw ModuloByZeroError("Modulo by zero");
    return Derived(value % other.value); 
}

template <typename Derived, typename T>
Derived NumericWrapper<Derived, T>::operator-() const {
    if constexpr (std::is_signed_v<T>) {
        if (value == std::numeric_limits<T>::min()) {
            throw OverflowError("Negation would overflow");
        }
    }
    return Derived(-value);
}

template <typename Derived, typename T>
Derived NumericWrapper<Derived, T>::operator+() const {
    return Derived(+value);  // Unary plus rarely needs overflow checking
}


// Compound arithmetic
template <typename Derived, typename T>
Derived& NumericWrapper<Derived, T>::operator+=(const Derived& other) { 
    value += other.value; 
    return static_cast<Derived&>(*this); 
}

template <typename Derived, typename T>
Derived& NumericWrapper<Derived, T>::operator-=(const Derived& other) { 
    value -= other.value; 
    return static_cast<Derived&>(*this); 
}

template <typename Derived, typename T>
Derived& NumericWrapper<Derived, T>::operator*=(const Derived& other) { 
    value *= other.value; 
    return static_cast<Derived&>(*this); 
}

template <typename Derived, typename T>
Derived& NumericWrapper<Derived, T>::operator/=(const Derived& other) { 
    if (other.value == 0) throw DivisionByZeroError("Division by zero");
    value /= other.value; 
    return static_cast<Derived&>(*this); 
}

template <typename Derived, typename T>
Derived& NumericWrapper<Derived, T>::operator%=(const Derived& other) { 
    if (other.value == 0) throw ModuloByZeroError("Modulo by zero");
    value &= other.value; 
    return static_cast<Derived&>(*this); 
}

// Comparisons
template <typename Derived, typename T>
bool NumericWrapper<Derived, T>::operator==(const Derived& other) const { 
    return value == other.value; 
}

template <typename Derived, typename T>
bool NumericWrapper<Derived, T>::operator!=(const Derived& other) const { 
    return value != other.value; 
}

template <typename Derived, typename T>
bool NumericWrapper<Derived, T>::operator<(const Derived& other) const { 
    return value < other.value; 
}

template <typename Derived, typename T>
bool NumericWrapper<Derived, T>::operator>(const Derived& other) const { 
    return value > other.value; 
}

template <typename Derived, typename T>
bool NumericWrapper<Derived, T>::operator<=(const Derived& other) const { 
    return value <= other.value; 
}

template <typename Derived, typename T>
bool NumericWrapper<Derived, T>::operator>=(const Derived& other) const { 
    return value >= other.value; 
}

// Bitwise operations
template <typename Derived, typename T>
template<typename U>
std::enable_if_t<std::is_integral_v<U>, Derived> 
NumericWrapper<Derived, T>::operator&(const Derived& other) const { 
    return Derived(value & other.value); 
}

template <typename Derived, typename T>
template<typename U>
std::enable_if_t<std::is_integral_v<U>, Derived> 
NumericWrapper<Derived, T>::operator|(const Derived& other) const { 
    return Derived(value | other.value); 
}

template <typename Derived, typename T>
template<typename U>
std::enable_if_t<std::is_integral_v<U>, Derived> 
NumericWrapper<Derived, T>::operator^(const Derived& other) const { 
    return Derived(value ^ other.value); 
}

template <typename Derived, typename T>
template<typename U>
std::enable_if_t<std::is_integral_v<U>, Derived> 
NumericWrapper<Derived, T>::operator~() const { 
    return Derived(~value); 
}

template <typename Derived, typename T>
template<typename U>
std::enable_if_t<std::is_integral_v<U>, Derived> 
NumericWrapper<Derived, T>::operator<<(int shift) const { 
    return Derived(value << shift); 
}

template <typename Derived, typename T>
template<typename U>
std::enable_if_t<std::is_integral_v<U>, Derived> 
NumericWrapper<Derived, T>::operator>>(int shift) const { 
    return Derived(value >> shift); 
}

// Assignment
template <typename Derived, typename T>
Derived& NumericWrapper<Derived, T>::operator=(T v) {
    value = v;
    return static_cast<Derived&>(*this);
}

// ==== CONTAINER WRAPPERS ====

// Homogenic container (similar to std::vector)
template<typename T>
class ListWrapper : public Wrapper<ListWrapper<T>> {
    std::vector<T> data;
public:
    using value_type = T;
    using iterator = typename std::vector<T>::iterator;
    using const_iterator = typename std::vector<T>::const_iterator;

    // Constructors
    ListWrapper() = default;
    explicit ListWrapper(std::vector<T>&& vec) : data(std::move(vec)) {}
    explicit ListWrapper(const std::vector<T>& vec) : data(vec) {}

    // Capacity
    size_t size() const noexcept { return data.size(); }
    bool empty() const noexcept { return data.empty(); }

    // Element access
    T& operator[](size_t index) { 
        if (index >= data.size()) throw IndexError("List index out of range");
        return data[index]; 
    }
    const T& operator[](size_t index) const { 
        if (index >= data.size()) throw IndexError("List index out of range");
        return data[index]; 
    }

    // Iterators
    iterator begin() noexcept { return data.begin(); }
    iterator end() noexcept { return data.end(); }
    const_iterator begin() const noexcept { return data.begin(); }
    const_iterator end() const noexcept { return data.end(); }

    // Modifiers
    void push_back(const T& value) { data.push_back(value); }
    void push_back(T&& value) { data.push_back(std::move(value)); }
    T pop_back() { 
        if (data.empty()) throw EmptyContainerError("Cannot pop from empty list");
        T val = std::move(data.back());
        data.pop_back();
        return val;
    }
};

// Heterogenic container (type-safe any values)
class CollectionWrapper : public Wrapper<CollectionWrapper> {
    std::vector<std::shared_ptr<Object>> items;
public:
    // Constructors
    CollectionWrapper() = default;
    
    // Capacity
    size_t size() const noexcept { return items.size(); }
    bool empty() const noexcept { return items.empty(); }

    // Type-safe element access
    template<typename T>
    std::shared_ptr<T> get(size_t index) const {
        if (index >= items.size()) throw IndexError("Collection index out of range");
        return std::dynamic_pointer_cast<T>(items[index]);
    }

    // Add items
    template<typename T>
    void add(std::shared_ptr<T> item) {
        items.push_back(item);
    }

    // Iterators
    auto begin() noexcept { return items.begin(); }
    auto end() noexcept { return items.end(); }
    auto begin() const noexcept { return items.begin(); }
    auto end() const noexcept { return items.end(); }
};

// Immutable heterogenic container (fixed-size)
template<typename... Ts>
class TupleWrapper : public Wrapper<TupleWrapper<Ts...>> {
    std::tuple<Ts...> data;
public:
    explicit TupleWrapper(Ts&&... args) : data(std::forward<Ts>(args)...) {}
    
    template<size_t I>
    auto& get() { return std::get<I>(data); }
    
    template<size_t I>
    const auto& get() const { return std::get<I>(data); }
    
    static constexpr size_t size() noexcept { return sizeof...(Ts); }
};

// Key-Value container
template<typename K, typename V>
class MapWrapper : public Wrapper<MapWrapper<K, V>> {
    std::map<K, V> data;

public:
    // ===== CONSTRUCTORS =====
    MapWrapper() = default;
    
    // Initializer list constructor
    explicit MapWrapper(std::initializer_list<std::pair<const K, V>> init) 
        : data(init) {}
        
    // Range constructor
    template<typename InputIt>
    MapWrapper(InputIt first, InputIt last) : data(first, last) {}
    
    // Copy/move constructors
    MapWrapper(const MapWrapper&) = default;
    MapWrapper(MapWrapper&&) noexcept = default;

    // ===== ASSIGNMENT OPERATORS =====
    MapWrapper& operator=(const MapWrapper&) = default;
    MapWrapper& operator=(MapWrapper&&) noexcept = default;
    
    // Initializer list assignment
    MapWrapper& operator=(std::initializer_list<std::pair<const K, V>> init) {
        data = init;
        return *this;
    }

    // ===== ELEMENT ACCESS ===== 
    V& operator[](const K& key) { return data[key]; }
    
    V& at(const K& key) { 
        try {
            return data.at(key);
        } catch (const std::out_of_range&) {
            throw KeyError("Key not found in map");
        }
    }
    
    const V& at(const K& key) const {
        try {
            return data.at(key);
        } catch (const std::out_of_range&) {
            throw KeyError("Key not found in map");
        }
    }

    // ===== CAPACITY =====
    size_t size() const noexcept { return data.size(); }
    bool empty() const noexcept { return data.empty(); }

    // ===== MODIFIERS =====
    void insert(const K& key, const V& value) { data[key] = value; }
    
    template<typename... Args>
    void emplace(Args&&... args) {
        data.emplace(std::forward<Args>(args)...);
    }
    
    bool erase(const K& key) { return data.erase(key) > 0; }
    void clear() noexcept { data.clear(); }

    // ===== LOOKUP =====
    bool contains(const K& key) const noexcept { 
        return data.find(key) != data.end(); 
    }

    // ===== ITERATORS =====
    auto begin() noexcept { return data.begin(); }
    auto end() noexcept { return data.end(); }
    auto begin() const noexcept { return data.begin(); }
    auto end() const noexcept { return data.end(); }
    auto cbegin() const noexcept { return data.cbegin(); }
    auto cend() const noexcept { return data.cend(); }

    // ===== CONVERSION =====
    std::map<K, V> to_std_map() const { return data; }
};
// Set type wrapper
template<typename T>
class SetWrapper : public Wrapper<SetWrapper<T>> {
    std::set<T> data;

public:
    using value_type = T;
    using iterator = typename std::set<T>::iterator;
    using const_iterator = typename std::set<T>::const_iterator;

    // Constructors
    SetWrapper() = default;
    explicit SetWrapper(std::set<T>&& s) : data(std::move(s)) {}
    explicit SetWrapper(const std::set<T>& s) : data(s) {}
    
    template<typename InputIt>
    SetWrapper(InputIt first, InputIt last) : data(first, last) {}

    // Capacity
    size_t size() const noexcept { return data.size(); }
    bool empty() const noexcept { return data.empty(); }

    // Modifiers
    void insert(const T& value) { data.insert(value); }
    void insert(T&& value) { data.insert(std::move(value)); }
    
    template<typename... Args>
    void emplace(Args&&... args) {
        data.emplace(std::forward<Args>(args)...);
    }

    bool erase(const T& value) { return data.erase(value) > 0; }
    void clear() noexcept { data.clear(); }

    // Lookup
    bool contains(const T& value) const noexcept {
        return data.find(value) != data.end();
    }

    // Set operations
  SetWrapper<T> operator&&(const SetWrapper<T>& other) const { // Intersection
        std::set<T> result;
        std::set_intersection(data.begin(), data.end(),
                            other.data.begin(), other.data.end(),
                            std::inserter(result, result.begin()));
        return SetWrapper<T>(std::move(result));
    }

    SetWrapper<T> operator||(const SetWrapper<T>& other) const { // Union
        std::set<T> result;
        std::set_union(data.begin(), data.end(),
                      other.data.begin(), other.data.end(),
                      std::inserter(result, result.begin()));
        return SetWrapper<T>(std::move(result));
    }

    SetWrapper<T> operator-(const SetWrapper<T>& other) const { // Difference
        std::set<T> result;
        std::set_difference(data.begin(), data.end(),
                          other.data.begin(), other.data.end(),
                          std::inserter(result, result.begin()));
        return SetWrapper<T>(std::move(result));
    }

    // Symmetric difference (a.k.a. disjunctive union)
    SetWrapper<T> operator^(const SetWrapper<T>& other) const {
        std::set<T> result;
        std::set_symmetric_difference(data.begin(), data.end(),
                                    other.data.begin(), other.data.end(),
                                    std::inserter(result, result.begin()));
        return SetWrapper<T>(std::move(result));
    }

    // Subset checks
    bool operator<=(const SetWrapper<T>& other) const { // Subset
        return std::includes(other.data.begin(), other.data.end(),
                           data.begin(), data.end());
    }

    bool operator>=(const SetWrapper<T>& other) const { // Superset
        return std::includes(data.begin(), data.end(),
                           other.data.begin(), other.data.end());
    }

    // Iterators
    iterator begin() noexcept { return data.begin(); }
    iterator end() noexcept { return data.end(); }
    const_iterator begin() const noexcept { return data.begin(); }
    const_iterator end() const noexcept { return data.end(); }

    // Conversion
    std::set<T> to_std_set() const { return data; }
};

// Variant type wrapper
template<typename... Ts>
using UnionWrapper = std::variant<Ts...>;

// Lambda type wrapper
template<typename Ret, typename... Args>
class LambdaWrapper : public Wrapper<LambdaWrapper<Ret, Args...>> {
    std::function<Ret(Args...)> func;

public:
    // Constructor from callable
    template<typename F>
    LambdaWrapper(F&& f) : func(std::forward<F>(f)) {}

    // Direct invocation with automatic conversion
    Ret operator()(typename Args::value_type... args) const {
        return func(Args(args)...);
    }

    // Dynamic invocation
    std::shared_ptr<Object> invoke(std::vector<std::shared_ptr<Object>> args) const {
        if (args.size() != sizeof...(Args)) {
            throw TypeError("Incorrect number of arguments");
        }
        return invoke_impl(args, std::index_sequence_for<Args...>{});
    }

private:
    template<size_t... I>
    std::shared_ptr<Object> invoke_impl(std::vector<std::shared_ptr<Object>>& args, 
                                      std::index_sequence<I...>) const {
        if constexpr (std::is_void_v<Ret>) {
            func(as<Args>(args[I])...);
            return nullptr;
        } else {
            return std::make_shared<Wrapper<Ret>>(func(as<Args>(args[I])...));
        }
    }
};

// Deduction guide for cleaner construction
template<typename Ret, typename... Args, typename F>
LambdaWrapper(F&& f) -> LambdaWrapper<Ret, Args...>;
// ==== CASTING FUNCTION ====
template <typename T, typename U>
T as(const U& obj) {
    if constexpr (std::is_convertible_v<U, T>) {
        return static_cast<T>(obj);
    } else {
        throw CastingError("Conversion failed");
    }
}

// Specialization for shared_ptr casting
template <typename T, typename U>
std::shared_ptr<T> as(const std::shared_ptr<U>& obj) {
    if (auto p = std::dynamic_pointer_cast<T>(obj)) {
        return p;
    }
    throw CastingError("Dynamic cast failed");
}

#endif // RUNTIME_HPP