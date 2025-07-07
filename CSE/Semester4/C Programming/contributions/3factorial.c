#include<stdio.h>
#include<stdlib.h>
void main()
{
    int n, fact = 1, i;
    printf("Enter a number : ");
    scanf("%d", &n);

    for(i = 1 ; i <= n ; i++)
    {
        fact *= i;
    }
    printf("Factorial = %d", fact);
}