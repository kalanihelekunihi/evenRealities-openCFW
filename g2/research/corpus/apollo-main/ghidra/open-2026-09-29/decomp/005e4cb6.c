
uint FUN_005e4cb6(ushort param_1,char param_2,char param_3,byte param_4)

{
  uint uVar1;
  
  uVar1 = (uint)param_1;
  if (param_2 != '\0') {
    uVar1 = uVar1 | 0x80000000;
  }
  if (param_3 != '\0') {
    uVar1 = uVar1 | 0x40000000;
  }
  return uVar1 | (uint)param_4 << 0x10;
}

