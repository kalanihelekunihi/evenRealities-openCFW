
void gx8002_uart_stage1_blkclr(void)

{
  uRam00000030 = 0;
  uRam0000006c = 0;
  gx8002_uart_stage1_pmu_dispatch(0x14,0,uRam00000040);
  gx8002_uart_stage1_pmu_dispatch(0x15,0);
  return;
}

