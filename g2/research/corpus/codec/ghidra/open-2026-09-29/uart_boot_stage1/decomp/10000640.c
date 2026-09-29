
uint gx8002_uart_stage1_get_char(void)

{
  do {
  } while ((((uint *)*puRam10000658)[5] & 1) == 0);
  return *(uint *)*puRam10000658 & 0xff;
}

