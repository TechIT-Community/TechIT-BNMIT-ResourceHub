#include<stdio.h>
#include<stdlib.h>
void main()
{
    int sum = 0, n, i = 1;
    printf("Enter the value of n : ");
    scanf("%d", &n);

    while(i <= n)
    {
        sum += i;
        i++;
    }

    printf("Sum = %d", sum);
}