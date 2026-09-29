
uint padmux_get(uint param_1)

{
  uint uVar1;
  int iVar2;
  
  if (param_1 < 0x21) {
    iVar2 = (param_1 & 7) << 2;
    uVar1 = (0xf << iVar2 & *(uint *)(((int)param_1 >> 3) * 4 + DAT_102065b4)) >> iVar2;
  }
  else {
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

