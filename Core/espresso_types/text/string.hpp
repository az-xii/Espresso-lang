#pragma once
#include "../base.hpp"
#include <string>
#include <vector>
#include <memory>

class EspressoString {
    std::unique_ptr<char32_t[]> data;
    size_t length;
    
public:
    // ============== CONSTRUCTORS ==============
    EspressoString() noexcept : data(nullptr), length(0) {}
    
    explicit EspressoString(const char* utf8);
    explicit EspressoString(const std::string& utf8);
    explicit EspressoString(std::u32string_view utf32);
    
    // ============== COPY/MOVE SEMANTICS ==============
    EspressoString(const EspressoString& other);
    EspressoString& operator=(const EspressoString& other);
    EspressoString(EspressoString&& other) noexcept;
    EspressoString& operator=(EspressoString&& other) noexcept;
    
    // ============== CHARACTER ACCESS ==============
    EspressoChar at(size_t pos) const;
    EspressoChar operator[](size_t pos) const noexcept;
    
    // ============== STRING OPERATIONS ==============
    EspressoString substr(size_t pos, size_t len = npos) const;
    EspressoString concat(const EspressoString& other) const;
    EspressoList<EspressoString> split(EspressoChar delim) const;
    EspressoString join(const EspressoList<EspressoString>& parts) const;
    
    // ============== SEARCH/COMPARE ==============
    EspressoBool contains(EspressoString substr) const noexcept;
    EspressoBool starts_with(EspressoString prefix) const noexcept;
    EspressoBool compare(const EspressoString& other) const noexcept;
    
    // ============== CONVERSIONS ==============
    std::string utf8() const;
    std::u16string utf16() const;
    const char32_t* utf32() const noexcept { return data.get(); }
    
    // ============== CAPACITY ==============
    size_t size() const noexcept { return length; }
    EspressoBool empty() const noexcept { return length == 0; }
    static const size_t npos = -1;
    
    // ============== ITERATORS ==============
    class iterator;
    iterator begin() const noexcept;
    iterator end() const noexcept;
    
    // ============== OPERATORS ==============
    EspressoBool operator==(const EspressoString& other) const noexcept;
    EspressoString operator+(const EspressoString& other) const;
    
    // ============== FRIEND FUNCTIONS ==============
    friend std::ostream& operator<<(std::ostream& os, const EspressoString& str);
    
private:
    // Helper functions
    EspressoVoid validate_range(size_t pos, const char* func) const;
    static std::u32string utf8_to_utf32(const char* utf8);
};

// ============== ITERATOR IMPLEMENTATION ==============
class EspressoString::iterator {
    const char32_t* ptr;
public:
    using iterator_category = std::random_access_iterator_tag;
    using value_type = EspressoChar;
    using difference_type = std::ptrdiff_t;
    using pointer = const EspressoChar*;
    using reference = const EspressoChar&;
    
    iterator(const char32_t* p) : ptr(p) {}
    
    // Iterator operations...
    EspressoChar operator*() const { return EspressoChar(*ptr); }
    iterator& operator++() { ++ptr; return *this; }
    EspressoBool operator!=(const iterator& other) const { return ptr != other.ptr; }
};

