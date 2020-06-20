/*
//int f = (g[1]) ? 12 : ((b) ? 2 : fake(a, b));
//int f = (((2) + fake(((a + b)), b)));
int ***b;
//foo g[6] = srand();
;

double a = g[2];
foo t[2*(12-3*3)*(12 + sizeof(int *))];

//g[3 - 1] = 12;
//struct foobar h = t->myFooVal;
void *v;
int *b = NULL;
long int **temp = 0 + b + (void *)g*(struct foobar *)5;

enum COLORS
{
    RED,
    BLUE,
    YELLOW
};

typedef struct
{
    int A;
    COLORS B;
} abEnum;

typedef long int * long_int_ptr;
*/

/*
enum NAMES
{
    GREG = 0,
    SHANNI,
    BOB = 5
};
*/

/*
int main(int a, int c)
{
    while(a)
        c += 2;

    do{
        c += 2;
    } while(a)

    a++;

    for(int a = 5;; a++);

    switch(a*c)
    {
        case 'A':
        case 'B':
            a = 3;
            break;
        default:
            a = 5;
            c = 2 + a;
        case 'C':
    }


    typedef double dbl;
    int a = 4;
    int *ptrA = &a;
    double b = (dbl)*ptrA;

    if (a) if (b) s(); else s2();

    while(a + c)
    {
        print();
        if(c)
            break;
        a += 3;
        else
            continue;
        c += 2;
    }

    struct myStruct
    {
        int a, *b, **c;
        long char d;
        char e, *f;
    };

    enum NAMES name = RED;

    union myUnion
    {
        int a;
        char b;
    };

    union myUnion cc;

    {
        int f = 6;
    }

    {
        int a = 5;
    }

    goto retLoc;
        break;
        continue;
    
    char b = '5', *c;
    int d = 32, *f = 12;
    int e[5];
    char g[6] = {'1', '2', '3', '4', '5', '\0'};
    char *str = "hello";
    int h[sizeof(g)];
    g[3] = 313;
    struct myStruct c = 12;
    b = (c*(2+3));
    char a = 42;
    int b = (4+(-2+5));
    retLoc:
    return 5;
}
int fake(int a,   char b)
{
    return 'f';
}
*/

union foo
{
    int a, **b, * const c[12];
    const int d;
    int e;
};

struct bar
{
    char a[12];
    int b;
    union foo myFoo[2];
};

int main() 
{ 
    const int * const number = 2, *numPtr = &number, val = 2;
    const int num = 3;
    const int *n = 5;
    char a ='A', b ='B';
    const char c, *d = &c; 
    char *const ptr = &a; 
    printf( "Value pointed to by ptr: %c\n", *ptr); 
    printf( "Address ptr is pointing to: %d\n\n", ptr); 
  
    //ptr = &b; illegal statement (assignment of read-only variable ptr) 
  
    // changing the value at the address ptr is pointing to 
    *ptr = b;  
    printf( "Value pointed to by ptr: %c\n", *ptr); 
    printf( "Address ptr is pointing to: %d\n", ptr); 

} 