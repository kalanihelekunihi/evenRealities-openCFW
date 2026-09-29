
uint FUN_005e4f02(ushort param_1,char param_2)

{
  uint uVar1;
  
  uVar1 = (uint)param_1;
  if (param_2 != '\0') {
    uVar1 = uVar1 | 0x80000000;
  }
  return uVar1;
}

