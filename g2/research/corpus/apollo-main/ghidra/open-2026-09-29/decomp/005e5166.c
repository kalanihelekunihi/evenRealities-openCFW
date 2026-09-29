
uint FUN_005e5166(byte param_1,ushort param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  iVar1 = DAT_005e5dd8;
  uVar2 = 0;
  if ((*(int *)(DAT_005e5dd8 + 4) != 0) &&
     (uVar2 = FUN_0044e498(*(undefined4 *)(DAT_005e5dd8 + 4)), (int)uVar2 < 0)) {
    uVar2 = 0;
  }
  if (*(char *)(iVar1 + 0x28c) == '\0') {
    uVar3 = 0;
  }
  else {
    uVar3 = 0x40000000;
  }
  return (param_1 & 0xf) << 0x14 | (param_2 & 0x3f) << 0x18 | uVar3 | uVar2 & 0xffff;
}

