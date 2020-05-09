void *temp = 0;

int main(int a, int c)
{
    struct myStruct
    {
        int a, *b, **c;
        long char d;
        char e, *f;
    };

    char b = '5', *c;
    int d = 32, *f = 12;
    int e[5];
    char g[6] = {'1', '2', '3', '4', '5', '\0'};
    int h[sizeof(g)];
    //g[3] = 313;
    struct myStruct c = 12;
    b = (c*(2+3));
    //char a = 42;
    //int b = (4+(-2+5));
    return 9-c;
}
/*
int fake(int a, char b)
{
    return 'f';
}
*/