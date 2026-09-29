
void FUN_005a0b54(char param_1)

{
  int iVar1;
  
  iVar1 = DAT_005a13d4;
  *DAT_005a13d0 = *DAT_005a13d0 & 0xffffffc0 | *(uint *)(DAT_005a13d4 + 0x68) >> 2 & 0x3f;
  *DAT_005a13cc = *DAT_005a13cc & 0xfffe7fff | (*(uint *)(iVar1 + 0x68) & 3) << 0xf;
  if (param_1 != '\0') {
    *DAT_005a13d8 = *DAT_005a13d8 - *DAT_005a16ec & 0x3ff | *DAT_005a13d8 & 0xfffffc00;
  }
  return;
}

