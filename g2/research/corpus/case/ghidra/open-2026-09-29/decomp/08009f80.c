
undefined4 case_verify_selector_bank(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int in_r3;
  int local_18;
  
  local_18 = in_r3;
  iVar1 = case_invoke_mode_one(8,&local_18);
  if (iVar1 == 0) {
    if ((char)local_18 != '\0') {
      return 1;
    }
    iVar2 = case_invoke_mode_one(0xb,&local_18);
    iVar1 = DAT_08009fec;
    if (iVar2 == 0) {
      if (-1 < local_18 << 0x18) {
        return 2;
      }
      iVar2 = 0;
      while (iVar3 = case_invoke_mode_one(iVar2 + 0x10U & 0xff,&local_18), iVar3 == 0) {
        if ((*(char *)(iVar1 + iVar2) != (char)local_18) || (iVar2 = iVar2 + 1, 0x4f < iVar2)) {
          if (iVar2 != 0x50) {
            return 3;
          }
          return 0;
        }
      }
    }
  }
  return 0xffffffff;
}

