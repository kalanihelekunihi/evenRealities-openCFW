
void gx8002_uart_stage1_postamble(void)

{
  int iVar1;
  
  iVar1 = *piRam10001dd4;
  *(uint *)(iVar1 + 0x3a0) = *(uint *)(iVar1 + 0x3a0) | 0x101;
  do {
  } while ((*(uint *)(iVar1 + 0x2c0) & 1) == 0);
  *(uint *)(iVar1 + 0x3a0) = *(uint *)(iVar1 + 0x3a0) & 0xfffffefe;
  *(undefined4 *)(iVar1 + 0x398) = 0;
  gx8002_uart_stage1_pmu_dispatch(0x19);
  return;
}

