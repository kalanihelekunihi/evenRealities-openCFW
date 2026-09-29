
void gx8002_uart_stage1_railcfg(void)

{
  int iVar1;
  
  gx8002_uart_stage1_pmu_dispatch(0x17,1);
  uRam00000010 = 0;
  uRam00000020 = 1;
  iVar1 = func_0x10000ea0(0x17);
  iRam00000024 = iVar1 / 1000000 + -1;
  uRam00000028 = 0;
  uRam00000010 = 2;
  return;
}

