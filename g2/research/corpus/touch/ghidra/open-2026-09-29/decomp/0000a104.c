
undefined4 Cy_SysClk_PeriphEnableDivider(uint param_1,uint param_2)

{
  undefined4 uVar1;
  
  if (((param_1 == 1) && (param_2 < 2)) ||
     ((uVar1 = DAT_0000a144, (param_1 - 2 & 0xff) < 2 && (param_2 == 0)))) {
    *DAT_0000a140 = (param_1 & 3) << 6 | param_2 & 0x3f | DAT_0000a13c;
    uVar1 = 0;
  }
  return uVar1;
}

