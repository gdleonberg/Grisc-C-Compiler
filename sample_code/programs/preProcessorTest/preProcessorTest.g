#ifdef __FILE__

#include "../../libraries/test/test.g"
#include "../../libraries/test2/test2.g"/* this
is a multi-line comment
*/
//#define test not1212
//\t\e\s\t is 
test;
#define test not1212 // actually works test
#define TOKENIZER "_"
//\t\e\s\t is 
test;
int main(int argc, char *argv[])
{
    printf("%d\n", __BASE_FILE__);
    printf("%d\n", __DATE__);
    printf("%d\n", __TIME__);
    printf("%d\n", __FILE__);
    printf("%d\n", __LINE__);
    printf("%d\n", TEST);
    printf("%d\n", TEST_TWO);
    printf("%d\n", TEST2);
    printf("%s\n", TOKENIZER); // comment

    #ifdef TOKENIZER
        printf("tokenizer defined");
        #ifdef test
            printf("both defined");
        #endif
        #ifndef test
            printf("Tokenizer defined but test not");
        #endif
    #endif
    #ifndef TOKENIZER
        #ifdef test
            printf("test defined but tokenizer not");
        #endif
    #endif

    #undef TOKENIZER
    printf("%s second time undefed at line %d\n", TOKENIZER, __LINE__);

    #ifdef TOKENIZER
    printf("TOKENIZER IS DEFINED");
    #endif

    #ifndef TOKENIZER
    printf("TOKENIZER IS NOT DEFINED");
    #endif
}
#endif

//test of this

/* begin multi-line but not finish
*/