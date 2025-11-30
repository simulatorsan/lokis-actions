#include <stdio.h>
#include <math.h>
#include <omp.h>
#include <stdlib.h>

// --- Hardcoded Input Constants ---
const double ll = 0.0;  // Lower limit of integration
const double ul = 10.0; // Upper limit of integration

// The function to be integrated. f(x) = 3x^2
double f(double x) {
    return 3.0 * x * x;
}

int main(int argc, char *argv[]) {
    const double TRUE_ANSWER = 1000.0;
    double h, integral_sum, integral_result, absolute_error;
    long n;
    int exponent;

    exponent = atoi(argv[1]);
    n = (long)pow(2, (double)exponent);

    h = (ul - ll) / (double)n;

    // Initialize the sum to 0.0 (using the Left Rectangular Rule)
    integral_sum = 0.0;

    printf("Starting integration of 3x^2 from %.1f to %.1f with %ld slices...\n", ll, ul, n);

    // --- Parallel Integration Loop (Left Rectangular Rule) ---
    // The sum of f(ll + i*h) for i from 0 to n-1
    // 'reduction(+:integral_sum)' safely adds each thread's partial sum
    // to the global 'integral_sum' variable.
    #pragma omp parallel for reduction(+:integral_sum)
    for (long i = 0; i < n; i++) {
        integral_sum += f(ll + (double)i * h);
    }

    // Final calculation: multiply the total sum by the step size (h)
    integral_result = h * integral_sum;
    
    // Calculate the absolute error
    absolute_error = fabs(TRUE_ANSWER - integral_result);

    printf("----------------------------------------\n");
    printf("True Answer:      %f\n", TRUE_ANSWER);
    printf("Calculated:       %f\n", integral_result);
    printf("Absolute Error:   %.12f x 1e-9\n", absolute_error*1000000000); // Display more precision for the error
    printf("----------------------------------------\n");

    return 0;
}
