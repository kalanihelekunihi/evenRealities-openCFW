
void WsfOsInit(void)

{
  int *piVar1;
  int iVar2;
  
  FUN_0043c0e4(DAT_0052bac4,0x40,0);
  piVar1 = DAT_0052babc;
  if (*DAT_0052babc == 0) {
    iVar2 = FUN_0047ebd8();
    *piVar1 = iVar2;
  }
  return;
}

