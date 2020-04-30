#ifndef test_g
#define test_g

#include "../test2/test2.g"
#include "test.g"

#define TEST (1212 + 13)
#define TEST_TWO 1

int fromtest();
int m_val = TEST;
int m_val2 = TEST_TWO;
char *m_val3 = __FILE__;
int m_val4 = __LINE__;

#endif