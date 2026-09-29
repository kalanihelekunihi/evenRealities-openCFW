
void touch_clock_12ac_validate(void)

{
  int iVar1;
  
  iVar1 = Cy_SysClk_ClkHfSetDivider(0);
  if (iVar1 != 0) {
    touch_runtime_12a6_fault(6);
  }
  *(uint *)(DAT_000045cc + 0x28) = *(uint *)(DAT_000045cc + 0x28) & 0xfffffff3;
  return;
}

