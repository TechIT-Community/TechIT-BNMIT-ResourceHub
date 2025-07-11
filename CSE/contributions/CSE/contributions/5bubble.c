#include<stdio.h>
#include<stdlib.h>
void main()
{
    int arr[25], n, i, j, temp;
    printf("Enter the number of elements : ");
    scanf("%d", &n);
    printf("Enter the elements : \n");
    for(i = 0 ; i < n ; i++)
    {
        scanf("%d", &arr[i]);
    }
    for(i = 0 ; i < n-1 ; i++)
    {
        for(j = 0 ; j < n-i-1 ; j++)
        {
            if(arr[j] > arr[j+1])
            {
                temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
    printf("The sorted array is : \n");
    for(i = 0 ; i < n ; i++)
    {
        printf("%d ", arr[i]);
    }
}