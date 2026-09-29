
uint touch_platform_13f8_rounded_measurement(void)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = *(uint *)(DAT_00004714 + 0x28) >> 6 & 3;
  iVar1 = Cy_SysClk_ClkHfGetFrequency();
  return iVar1 + ((uint)(1 << uVar2) >> 1) >> uVar2;
}

