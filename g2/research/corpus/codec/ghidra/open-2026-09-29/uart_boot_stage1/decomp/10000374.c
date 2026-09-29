
void gx8002_uart_stage1_pmu_set_bit0(uint param_1)

{
  uRam00000030 = param_1 & 1 | uRam00000030 & 0xfffffffe;
  return;
}

