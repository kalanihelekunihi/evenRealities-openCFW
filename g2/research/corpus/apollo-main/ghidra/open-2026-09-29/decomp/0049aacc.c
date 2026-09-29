
void FUN_0049aacc(int param_1)

{
  int iVar1;
  
  if (*(int *)(param_1 + 0x34) != -1) {
    for (iVar1 = 0; (iVar1 < 4 && (*(char *)(param_1 + iVar1 + 0x30) != '\0')); iVar1 = iVar1 + 1) {
      *(undefined1 *)(*(int *)(param_1 + 0x2c) + iVar1 + *(int *)(param_1 + 0x34)) =
           *(undefined1 *)(param_1 + iVar1 + 0x30);
    }
    *(undefined4 *)(param_1 + 0x34) = 0xffffffff;
  }
  return;
}

