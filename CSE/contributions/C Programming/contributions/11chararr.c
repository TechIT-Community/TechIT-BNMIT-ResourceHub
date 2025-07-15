#include <stdio.h>

void acceptCharacters(char *array, int n);

int main() 
{
    int n;
    char charArray[30];
    printf("Enter the number of characters: ");
    scanf("%d", &n);
    //char charArray[n];
    acceptCharacters(charArray, n);

    printf("\nCharacters entered: ");
    for (int i = 0; i < n; i++) {
        printf("%c ", charArray[i]);
    }

    return 0;
}

void acceptCharacters(char *array, int n) {
    printf("Enter %d characters:\n", n);

    for (int i = 0; i < n; i++) {
        scanf(" %c", array + i);
    }
}
