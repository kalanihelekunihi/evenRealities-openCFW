
void touch_clock_12d0_transition(void)

{
  int iVar1;
  
  power_mode_set(0x30);
  iVar1 = DAT_00004628;
  *(undefined4 *)(DAT_00004628 + 0x30) = 0x80000000;
  Cy_SysClk_ImoSetFrequency(DAT_0000462c);
  Cy_SysClk_ClkHfSetDivider(0);
  *(uint *)(iVar1 + 0x28) = *(uint *)(iVar1 + 0x28) & 0xfffffff3;
  *(uint *)(iVar1 + 0x28) = *(uint *)(iVar1 + 0x28) & 0xffffff3f;
  touch_clock_1434_calibrate();
  Cy_SysClk_ClkHfSetSource(0);
  *(uint *)(iVar1 + 0x2c) = *(uint *)(iVar1 + 0x2c) | 0x80000000;
  Cy_SysClk_ImoSetFrequency(DAT_00004630);
  touch_clock_12ac_validate();
  *(uint *)(iVar1 + 0x28) = *(uint *)(iVar1 + 0x28) & 0xffffff3f;
  power_mode_set(0x30);
  touch_clock_1434_calibrate();
  return;
}

