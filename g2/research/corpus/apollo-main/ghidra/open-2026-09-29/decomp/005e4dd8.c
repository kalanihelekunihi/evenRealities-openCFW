
uint FUN_005e4dd8(ushort param_1,char param_2,char param_3,char param_4,char param_5)

{
  uint uVar1;
  
  uVar1 = (uint)param_1;
  if (param_2 != '\0') {
    uVar1 = uVar1 | 0x80000000;
  }
  if (param_3 != '\0') {
    uVar1 = uVar1 | 0x40000000;
  }
  if (param_4 != '\0') {
    uVar1 = uVar1 | 0x20000000;
  }
  if (param_5 != '\0') {
    uVar1 = uVar1 | 0x10000000;
  }
  return uVar1;
}

