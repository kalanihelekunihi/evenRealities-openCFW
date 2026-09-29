
void FUN_004ab004(char param_1)

{
  int iVar1;
  
  FUN_0045a568();
  if (param_1 == '\v') {
    iVar1 = FUN_0043fd9e(*DAT_004abc00);
    FUN_0043f506(*DAT_004ab068,0x1d7 - iVar1);
    FUN_0043f6b8(*DAT_004abba0,6,0xfffffff8,0xfffffff0);
  }
  else {
    FUN_0043f506(*DAT_004ab068,0x3fffffff);
    FUN_0043f6b8(*DAT_004abba0,5,0,0xfffffff0);
  }
  return;
}

