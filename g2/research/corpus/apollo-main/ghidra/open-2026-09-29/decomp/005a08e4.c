
undefined4 FUN_005a08e4(void)

{
  bool bVar1;
  byte bVar2;
  uint *puVar3;
  
  puVar3 = DAT_005a0a58;
  if (((*DAT_005a0a58 & 0xff) == 0x21) && (*DAT_005a0a5c == 2)) {
    *DAT_005a0a34 = 1;
  }
  else {
    *DAT_005a0a34 = 0;
  }
  if (((((*puVar3 & 0xff) == 0x21) && (*DAT_005a0a5c == 2)) ||
      (((*puVar3 & 0xff) == 0x21 && (*DAT_005a0a5c == 3)))) ||
     (((*puVar3 & 0xff) == 0x22 && (*DAT_005a0a5c == 0)))) {
    *DAT_005a09d0 = 1;
  }
  else {
    *DAT_005a09d0 = 0;
  }
  if (((*puVar3 & 0xff) == 0x22) && (*DAT_005a0a5c == 1)) {
LAB_005a09b2:
    *DAT_005a0a68 = 1;
  }
  else {
    if (((*puVar3 & 0xff) == 0x23) && (*DAT_005a0a5c == 0)) {
      if ((((*(uint *)(DAT_005a0a60 + 0x44) & DAT_005a0a64) == 0x31800000) &&
          (0x13 < (*(uint *)(DAT_005a0a60 + 0x44) & 0x1fffff) >> 0x10)) &&
         ((*(uint *)(DAT_005a0a60 + 0x44) & 0xffff) == 0)) {
        bVar1 = true;
      }
      else {
        if (((*(uint *)(DAT_005a0a60 + 0x44) & 0x3fffffff) >> 0x19 < 0x19) ||
           ((*(uint *)(DAT_005a0a60 + 0x44) & 0xffff) != 0)) {
          bVar2 = 1;
        }
        else {
          bVar2 = 0;
        }
        bVar1 = (bool)(bVar2 ^ 1);
      }
      if (!bVar1) goto LAB_005a09b2;
    }
    *DAT_005a0a68 = 0;
  }
  return 0;
}

