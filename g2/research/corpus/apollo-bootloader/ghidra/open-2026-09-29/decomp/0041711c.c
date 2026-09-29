
void FUN_0041711c(int param_1)

{
  int iVar1;
  int iVar2;
  
  *(int *)(param_1 + 8) = param_1;
  *(int *)(param_1 + 0xc) = param_1;
  *(undefined4 *)(param_1 + 0x10) = 0;
  for (iVar1 = 0; iVar1 < 0x18; iVar1 = iVar1 + 1) {
    *(undefined4 *)(param_1 + iVar1 * 4 + 0x14) = 0;
    for (iVar2 = 0; iVar2 < 0x20; iVar2 = iVar2 + 1) {
      *(int *)(iVar1 * 0x80 + param_1 + iVar2 * 4 + 0x74) = param_1;
    }
  }
  return;
}

