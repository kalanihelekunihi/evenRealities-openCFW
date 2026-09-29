
void FUN_0800c0b8(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  uint uVar2;
  
  iVar1 = DAT_0800c0dc;
  uVar2 = 0;
  do {
    if (*(int *)(DAT_0800c0dc + uVar2 * 8) == 0) {
      *(undefined4 *)(DAT_0800c0dc + uVar2 * 8) = param_2;
      *(undefined4 *)(uVar2 * 8 + iVar1 + 4) = param_1;
      return;
    }
    uVar2 = uVar2 + 1;
  } while (uVar2 < 8);
  return;
}

