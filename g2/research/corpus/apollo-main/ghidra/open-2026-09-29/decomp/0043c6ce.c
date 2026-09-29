
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0043c6ce(void)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  
  piVar2 = _DAT_0043c7b4;
  piVar1 = _DAT_0043c794;
  if (*_DAT_0043c798 == '\0') {
    FUN_0043c5f6();
  }
  else if (*_DAT_0043c794 != 0) {
    *_DAT_0043c7b4 = (*_DAT_0043c7b4 + 1) % 6;
    FUN_0043f09a(*piVar1,0,*piVar2 * 0x30);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0043c764,DAT_0043c760,_DAT_0043c7c4,0x9c,PTR_DAT_0043c7c0,*piVar2,
                   *piVar2 * 0x30);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10800000,_DAT_0043c7c8,_DAT_0043c7c8,*piVar2,*piVar2 * 0x30);
    }
  }
  return;
}

