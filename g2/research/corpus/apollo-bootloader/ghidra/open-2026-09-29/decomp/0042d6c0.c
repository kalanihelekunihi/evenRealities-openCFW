
undefined4 bl_bl009_dispatch(void)

{
  bool bVar1;
  byte bVar2;
  uint *puVar3;
  
  puVar3 = DAT_0042d834;
  if (((*DAT_0042d834 & 0xff) == 0x21) && (*DAT_0042d838 == 2)) {
    *DAT_0042d810 = 1;
  }
  else {
    *DAT_0042d810 = 0;
  }
  if (((((*puVar3 & 0xff) == 0x21) && (*DAT_0042d838 == 2)) ||
      (((*puVar3 & 0xff) == 0x21 && (*DAT_0042d838 == 3)))) ||
     (((*puVar3 & 0xff) == 0x22 && (*DAT_0042d838 == 0)))) {
    *DAT_0042d7ac = 1;
  }
  else {
    *DAT_0042d7ac = 0;
  }
  if (((*puVar3 & 0xff) == 0x22) && (*DAT_0042d838 == 1)) {
LAB_0042d78e:
    *DAT_0042d844 = 1;
  }
  else {
    if (((*puVar3 & 0xff) == 0x23) && (*DAT_0042d838 == 0)) {
      if ((((*(uint *)(DAT_0042d83c + 0x44) & DAT_0042d840) == 0x31800000) &&
          (0x13 < (*(uint *)(DAT_0042d83c + 0x44) & 0x1fffff) >> 0x10)) &&
         ((*(uint *)(DAT_0042d83c + 0x44) & 0xffff) == 0)) {
        bVar1 = true;
      }
      else {
        if (((*(uint *)(DAT_0042d83c + 0x44) & 0x3fffffff) >> 0x19 < 0x19) ||
           ((*(uint *)(DAT_0042d83c + 0x44) & 0xffff) != 0)) {
          bVar2 = 1;
        }
        else {
          bVar2 = 0;
        }
        bVar1 = (bool)(bVar2 ^ 1);
      }
      if (!bVar1) goto LAB_0042d78e;
    }
    *DAT_0042d844 = 0;
  }
  return 0;
}

