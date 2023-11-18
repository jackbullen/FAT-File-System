//
// mkfile.c
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 512
#define BLOCK_COUNT 5

int main ( int argc, char *argv[] )
{
    char buffer[BUFFER_SIZE];
    int blockCount = BLOCK_COUNT;
    char ch = 'A';

    // char c[4] = "abc";
    // char ah = 'a';
    // printf("%s\n", c);
    // printf("%c\n", c);
    // printf("%c\n", *c);
    // printf("%c\n", ah);
    // printf("%p\n", c);

    if ( argc != 4 )
    {
        printf("argc = %d : Usage: makefile filename size character\n", argc);
        return 0;
    }

    FILE *file = fopen (argv[1], "wb");

    if ( !file ) 
    {
        printf("Couldn't create: %s\n", argv[1]);
        return 0;
    }

    if ( argv[2] )
        blockCount = atoi(argv[2]);

    if ( argv[3] )
        ch = argv[3][0];

    for ( int i = 0; i < blockCount; i++ )
    {
        memset (buffer, (int)ch, BUFFER_SIZE);
        fwrite (buffer, BUFFER_SIZE, 1, file);
        ch++;
    }

    fclose (file);

    return 0;
}