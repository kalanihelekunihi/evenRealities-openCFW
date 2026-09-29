
void FUN_005ea30c(void)

{
  int iVar1;
  
  iVar1 = DAT_005eadb4;
  if (*(int *)(DAT_005eadb4 + 0x1e0) != 0) {
    FUN_0044d7b8(*(undefined4 *)(DAT_005eadb4 + 0x1e0));
  }
  *(undefined4 *)(iVar1 + 0x1e0) = 0;
  *(undefined4 *)(iVar1 + 0x1e4) = 0;
  *(undefined4 *)(iVar1 + 0x1e8) = 0;
  *(undefined4 *)(iVar1 + 0x1ec) = 0;
  *(undefined4 *)(iVar1 + 0x1f0) = 0;
  return;
}

