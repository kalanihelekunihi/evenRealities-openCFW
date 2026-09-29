
void FUN_005ec9c0(void)

{
  int iVar1;
  
  iVar1 = DAT_005ec9e8;
  if (*(int *)(DAT_005ec9e8 + 0x224) != 0) {
    FUN_0044d7b8(*(undefined4 *)(DAT_005ec9e8 + 0x224));
    *(undefined4 *)(iVar1 + 0x224) = 0;
    *(undefined4 *)(iVar1 + 0x228) = 0;
    *(undefined4 *)(iVar1 + 0x22c) = 0;
  }
  return;
}

