
undefined4 Cy_SysClk_PeriphAssignDivider(uint param_1,uint param_2,uint param_3)

{
  undefined4 uVar1;
  
  uVar1 = DAT_0000a100;
  if ((param_1 < 4) &&
     (((param_2 == 1 && (param_3 < 2)) || (((param_2 - 2 & 0xff) < 2 && (param_3 == 0)))))) {
    *(uint *)((param_1 + 0x40) * 4 + DAT_0000a0fc) = (param_2 & 3) << 6 | param_3 & 0x3f;
    uVar1 = 0;
  }
  return uVar1;
}

