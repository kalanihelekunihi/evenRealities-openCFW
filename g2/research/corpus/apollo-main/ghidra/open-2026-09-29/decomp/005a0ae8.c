
void FUN_005a0ae8(char param_1)

{
  uint *puVar1;
  uint uVar2;
  
  if (param_1 != '\0') {
    *DAT_005a13cc = *DAT_005a13cc | 0x18000;
    *DAT_005a13d0 = *DAT_005a13d0 & 0xffffffc0 | *(uint *)(DAT_005a13d4 + 0x68) >> 0xe & 0x3f;
  }
  puVar1 = DAT_005a13d8;
  if ((*DAT_005a13d8 & 0x3ff) + 7 < 0x400) {
    *DAT_005a16ec = 7;
  }
  else {
    *DAT_005a16ec = 0x3ff - (*DAT_005a13d8 & 0x3ff);
  }
  uVar2 = *puVar1;
  *puVar1 = *DAT_005a16ec + uVar2 & 0x3ff | uVar2 & 0xfffffc00;
  return;
}

