#include "runtime.hpp"

// ===== ERROR CLASS IMPLEMENTATIONS =====
Error::Error(const std::string& msg) : message(msg) {}

const char* Error::what() const noexcept { 
    return message.c_str(); 
}

// ===== OBJECT CLASS IMPLEMENTATIONS =====
const std::type_info& Object::type() const noexcept {
    return typeid(Object);
}

// ===== STRING CLASS IMPLEMENTATIONS =====

// Helper function for UTF-8 codepoint counting
static size_t utf8_codepoint_count(const std::string& s) {
    size_t i = 0, count = 0, n = s.size();
    while (i < n) {
        unsigned char c = static_cast<unsigned char>(s[i]);
        int width = 1;
        if (c < 0x80) width = 1;
        else if ((c & 0xE0) == 0xC0) width = 2;
        else if ((c & 0xF0) == 0xE0) width = 3;
        else if ((c & 0xF8) == 0xF0) width = 4;
        else throw EncodingError("Invalid UTF-8 leading byte");
        
        if (i + width > n) throw EncodingError("Truncated UTF-8 sequence");
        
        // Validate continuation bytes
        for (int k = 1; k < width; ++k) {
            unsigned char cc = static_cast<unsigned char>(s[i + k]);
            if ((cc & 0xC0) != 0x80) throw EncodingError("Invalid UTF-8 continuation byte");
        }
        
        i += width;
        count++;
    }
    return count;
}

// StringWrapper constructors
StringWrapper::StringWrapper() = default;

StringWrapper::StringWrapper(const std::string& s) : data(s) {}

StringWrapper::StringWrapper(std::string&& s) noexcept : data(std::move(s)) {}

StringWrapper::StringWrapper(const char* s) : data(s ? s : "") {}

// StringWrapper accessors
const std::string& StringWrapper::str() const noexcept { 
    return data; 
}

size_t StringWrapper::length_bytes() const noexcept { 
    return data.size(); 
}

size_t StringWrapper::length() const {
    return utf8_codepoint_count(data);
}

bool StringWrapper::empty() const noexcept { 
    return data.empty(); 
}

// StringWrapper iterators
StringWrapper::iterator StringWrapper::begin() { 
    return data.begin(); 
}

StringWrapper::iterator StringWrapper::end() { 
    return data.end(); 
}

StringWrapper::const_iterator StringWrapper::begin() const { 
    return data.begin(); 
}

StringWrapper::const_iterator StringWrapper::end() const { 
    return data.end(); 
}

// StringWrapper C-style access
const char* StringWrapper::c_str() const noexcept { 
    return data.c_str(); 
}

// StringWrapper UTF-8 operations
std::string StringWrapper::utf8() const noexcept { 
    return data; 
}

char32_t StringWrapper::at(size_t index) const {
    size_t i = 0, cp_index = 0, n = data.size();
    
    while (i < n) {
        unsigned char c = static_cast<unsigned char>(data[i]);
        int width = 1;
        char32_t codepoint = 0;

        // Decode UTF-8 sequence
        if (c < 0x80) { 
            width = 1; 
            codepoint = c; 
        }
        else if ((c & 0xE0) == 0xC0) { 
            width = 2; 
            codepoint = c & 0x1F; 
        }
        else if ((c & 0xF0) == 0xE0) { 
            width = 3; 
            codepoint = c & 0x0F; 
        }
        else if ((c & 0xF8) == 0xF0) { 
            width = 4; 
            codepoint = c & 0x07; 
        }
        else {
            throw EncodingError("Invalid UTF-8 leading byte");
        }

        if (i + width > n) {
            throw EncodingError("Truncated UTF-8 sequence");
        }

        // Process continuation bytes
        for (int k = 1; k < width; ++k) {
            unsigned char cc = static_cast<unsigned char>(data[i + k]);
            if ((cc & 0xC0) != 0x80) {
                throw EncodingError("Invalid UTF-8 continuation byte");
            }
            codepoint = (codepoint << 6) | (cc & 0x3F);
        }

        // Check if this is the requested codepoint
        if (cp_index == index) {
            return codepoint;
        }
        
        i += width;
        cp_index++;
    }
    
    throw StringIndexError("Codepoint index out of range");
}

// StringWrapper validation
bool StringWrapper::is_valid_utf8(const std::string& s) noexcept {
    size_t i = 0, n = s.size();
    while (i < n) {
        unsigned char c = static_cast<unsigned char>(s[i]);
        if (c < 0x80) { 
            i += 1; 
            continue; 
        }
        
        int width = 0;
        if ((c & 0xE0) == 0xC0) width = 2;
        else if ((c & 0xF0) == 0xE0) width = 3;
        else if ((c & 0xF8) == 0xF0) width = 4;
        else return false;
        
        if (i + width > n) return false;
        
        for (int k = 1; k < width; ++k) {
            unsigned char cc = static_cast<unsigned char>(s[i + k]);
            if ((cc & 0xC0) != 0x80) return false;
        }
        
        i += width;
    }
    return true;
}

// ===== TEST AND DEMONSTRATION FUNCTIONS =====
void test_runtime_system() {
    try {
        std::cout << "=== Runtime System Test ===" << std::endl;
        
        // Test StringWrapper
        StringWrapper str("Hello, 世界! 🌟");
        std::cout << "String: " << str.str() << std::endl;
        std::cout << "Byte length: " << str.length_bytes() << std::endl;
        std::cout << "Codepoint length: " << str.length() << std::endl;
        
        // Test codepoint access
        try {
            for (size_t i = 0; i < str.length(); ++i) {
                char32_t cp = str.at(i);
                std::cout << "Codepoint " << i << ": U+" << std::hex << cp << std::dec << std::endl;
            }
        } catch (const StringIndexError& e) {
            std::cout << "String index error: " << e.what() << std::endl;
        }
        
        std::cout << "\n--- Numeric Tests ---" << std::endl;
        
        // Test NumericWrapper
        IntWrapper a(42);
        IntWrapper b(8);
        IntWrapper c = a + b;
        std::cout << "42 + 8 = " << c << std::endl;
        
        // Test bitwise operations (only works with integral types)
        IntWrapper x(12);  // 1100 in binary
        IntWrapper y(10);  // 1010 in binary
        IntWrapper z = x & y;  // Should be 8 (1000 in binary)
        std::cout << "12 & 10 = " << z << std::endl;
        
        // Test division by zero
        IntWrapper zero(0);
        try {
            IntWrapper result = a / zero;
        } catch (const DivisionByZeroError& e) {
            std::cout << "Caught expected error: " << e.what() << std::endl;
        }
        
        // Test overflow detection
        try {
            ByteWrapper small_num(100);
            ByteWrapper big_result = small_num * ByteWrapper(3);  // Should be fine (300 might overflow int8_t)
            std::cout << "100 * 3 = " << big_result << std::endl;
        } catch (const OverflowError& e) {
            std::cout << "Overflow caught: " << e.what() << std::endl;
        }
        
        // Test floating point operations
        FloatWrapper f1(3.14f);
        FloatWrapper f2(2.0f);
        FloatWrapper f3 = f1 * f2;
        std::cout << "3.14 * 2.0 = " << f3 << std::endl;
        
        // Note: Bitwise operations are not available for FloatWrapper
        // FloatWrapper f4 = f1 & f2;  // This would cause a compile error!
        
    } catch (const Error& e) {
        std::cout << "Error: " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cout << "Standard exception: " << e.what() << std::endl;
    }
}