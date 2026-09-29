
void FUN_004bb21c(int param_1)

{
  int iVar1;
  
  if ((((param_1 != 0) && (*(char *)(param_1 + 0x31) != '\0')) &&
      (*(char *)(param_1 + 0x32) == '\0')) && (iVar1 = FUN_0047ae78(param_1,4,0), iVar1 != 0)) {
    DmPrivSetPrivacyMode(*(undefined1 *)(iVar1 + 0x16),iVar1 + 0x10,1);
    FUN_0047b4ce(param_1,0);
  }
  return;
}

