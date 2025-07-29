class Vector {
    EspressoFloat x, y;
    public:
    void Vector(EspressoFloat x = 0, EspressoFloat y = 0) {
        this.x = x;
        this.y = y;
    }
    EspressoFloat magnitude() {
        return float(math::sqrt(this.x * this.x + this.y * this.y));
    }
    Vector operator+(Vector other) {
        return Vector(this.x + other.x, this.y + other.y);
    }
    EspressoString ToString() {
        return fmt::format("Vector({1}, {3})", this.x, this.y);
    }
};
EspressoInt CalcFactorial(EspressoInt n) {
    if (!isinstance(n, int) || n < 0) {
        throw ValueError("Input must be non-negative integer");
    } else {
        return n <= 1 ? 1 : n * CalcFactorial(n - 1);
    }
}
EspressoString RiskyOperation() {
    if (random::Random() > 0.5) {
        throw RuntimeError("Random failure!");
    } else {
        return "Success";
    }
}
EspressoInt Main() {
    Vector  v1 = Vector(3, 4);
    Vector  v2 = Vector(2, 5);
    print(fmt::format("Vector sum: {1}", v1 + v2));
    print(fmt::format("Magnitude: {1}", v1.magnitude():.2f));
    try {
        print(fmt::format("Factorial of 5: {1}", CalcFactorial(5)));
        print(fmt::format("Factorial of -1: {1}", CalcFactorial(-1)));
    } catch (ValueError e) {
        print(fmt::format("Error: {1}", ValueError::what()));
    }
    for (EspressoInt  i = 0;; i < 3; i += 1) {
        try {
            print(risky_operation());
        } catch (RuntimeError e) {
            print(fmt::format("Caught exception: {1}", RuntimeError::what()));
        }
    }
}