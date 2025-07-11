#include<stdio.h>
#include<stdlib.h>
void main()
{
    char job_band;
    printf("Enter your job band : \n");
    scanf("%c", &job_band);
    
    switch(job_band)
    {
        case 'A' : 
        {
            printf("Basic salary = 10,000 INR");
            break;
        }
        case 'B' : 
        {
            printf("Basic salary = 15,000 INR");
            break;
        }
        case 'C' : 
        {
            printf("Basic salary = 35,000 INR");
            break;
        }
        case 'D' : 
        {
            printf("Basic salary = 50,000 INR");
            break;
        }
        default : 
        {
            printf("INCORRECT JOB BAND");
        }
    }
}