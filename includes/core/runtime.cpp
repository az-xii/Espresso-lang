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
    size_t count = 0;
    for (size_t i = 0; i < s.size(); ) {
        unsigned char c = static_cast<unsigned char>(s[i]);
        
        if (c < 0x80) {
            i += 1;
        } else if ((c & 0xE0) == 0xC0) {
            if (i + 1 >= s.size() || (s[i+1] & 0xC0) != 0x80) {
                throw EncodingError("Invalid UTF-8 sequence");
            }
            i += 2;
        } else if ((c & 0xF0) == 0xE0) {
            if (i + 2 >= s.size() || (s[i+1] & 0xC0) != 0x80 || (s[i+2] & 0xC0) != 0x80) {
                throw EncodingError("Invalid UTF-8 sequence");
            }
            i += 3;
        } else if ((c & 0xF8) == 0xF0) {
            if (i + 3 >= s.size() || (s[i+1] & 0xC0) != 0x80 || 
                (s[i+2] & 0xC0) != 0x80 || (s[i+3] & 0xC0) != 0x80) {
                throw EncodingError("Invalid UTF-8 sequence");
            }
            i += 4;
        } else {
            throw EncodingError("Invalid UTF-8 leading byte");
        }
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

