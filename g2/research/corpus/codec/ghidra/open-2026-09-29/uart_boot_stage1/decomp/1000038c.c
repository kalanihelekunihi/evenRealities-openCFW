
void gx8002_uart_stage1_pmu_set_bit1(uint param_1)

{
  uRam00000030 = (param_1 & 1) << 1 | uRam00000030 & 0xfffffffd;
  return;
}

