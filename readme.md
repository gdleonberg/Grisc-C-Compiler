  # Stripped-Down ANSI C (C89) Compiler for GRISC ISA

  ###### (Uses self auto-generated recursive descent with backtracking parser)

  * Proof-of-concept

  * Very time and memory inefficient, I have no desire to improve performance of compiler or of generated assembly

  * Intended to support all ANSI C (C89) language features except the list below.

    * auto (unnecesarry)
    * register (only exists to guide compiler optimization)
    * extern
    * volatile (due to lack of optimizations all variables are already treated as volatile)
    * varargs using ...

  * Adds C99-style single line comments using '//'