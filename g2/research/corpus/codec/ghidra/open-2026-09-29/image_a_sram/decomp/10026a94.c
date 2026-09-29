
/* WARNING: Control flow encountered bad instruction data */

void gx8002_uart_descriptors(int param_1)

{
  stub();
  stub();
  stub();
  *(char *)(param_1 + 0x10) = (char)param_1;
  stub();
  stub();
  stub();
  stub();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

