
void FUN_00597dec(void)

{
  int iVar1;
  
  iVar1 = FUN_00597e1c();
  if (-1 < iVar1) {
    iVar1 = FUN_00597cae();
  }
  if ((iVar1 < 1) || (*DAT_00597e18 != '\0')) {
    if (iVar1 < 1) {
      *DAT_00597e18 = '\0';
    }
  }
  else {
    *DAT_00597e18 = '\x01';
  }
  return;
}

