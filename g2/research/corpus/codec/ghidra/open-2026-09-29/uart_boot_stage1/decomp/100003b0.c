
uint gx8002_uart_stage1_pmu_get_bit1(void)

{
  return uRam00000030 >> 1 & 1;
}

