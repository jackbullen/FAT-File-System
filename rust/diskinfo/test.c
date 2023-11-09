#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main(int argc, char* argv[]) {
    #if defined(_WIN32) || defined(_WIN64)
        printf("Windows\n");
    #elif defined(__linux__)
        printf("Linux\n");
    #elif defined(__APPLE__)
        printf("MacOS\n");
    #endif
    return 0;
}