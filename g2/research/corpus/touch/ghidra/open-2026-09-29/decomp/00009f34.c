
uint Cy_SysClk_ClkHfGetDivider(void)

{
  return *(uint *)(DAT_00009f40 + 0x28) & 3;
}

