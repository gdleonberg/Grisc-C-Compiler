  # Stripped-Down ANSI C (C89) Compiler for GRISC ISA

  ###### (Uses self auto-generated recursive descent with backtracking parser)

  * Proof-of-concept

  * Very time and memory inefficient, I have no desire to improve performance of compiler or of generated assembly

  * Intended to support all ANSI C (C89) language features except the list below.

    * auto (unnecesarry)
    * register (only exists to guide compiler optimization)
    * extern
    * static
    * volatile (due to lack of optimizations all variables are already treated as volatile)
    * varargs using ... (printf will still work because functions can be passed extra arguments without breaking semantic analysis)
    * initializer lists
    * empty arrays (ie char *argv[] must be written as char **argv)
    * arrays must be declared and assigned in separate statements
    * all type qualifiers must go before the type (ie "const int" is allowed but not "int const")
    * only primitives are [bool, char, unsigned char, short, unsigned short, int, unsigned int, long, unsigned long, float, double]

  * Type casting requires the operand to be in parentheses to avoid grammar context-sensitivity (aka the lexer hack)
  * Ternary statements are in the form "(expression) ? expression : expression", requiring parantheses for the condition
  * Adds C99-style single line comments using '//'
  * Adds bool integral type from C99
  * Adds ability from C99 to declare variables anywhere, not just top of scope block