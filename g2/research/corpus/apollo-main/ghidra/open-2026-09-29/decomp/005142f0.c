
void FUN_005142f0(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  if (param_1 != 0) {
    if ((*(int *)(param_1 + 0x24) != 0) && (-1 < (int)((uint)*(byte *)(param_1 + 0x18) << 0x1a))) {
      param_1 = *(int *)(param_1 + 0x24);
    }
    do {
      iVar2 = *DAT_00514b78;
      iVar1 = *(int *)(iVar2 + 4);
      if (iVar1 == param_1) {
        if (iVar1 == 0) {
          *(undefined4 *)(iVar2 + 4) = 0;
        }
        else {
          iVar3 = *(int *)(iVar1 + 0x14);
          if (iVar3 + 2 <= *(int *)(iVar1 + 0x10)) {
            iVar4 = *(int *)(iVar1 + 8);
            *(undefined4 *)(iVar4 + iVar3 * 4) = 0x50000;
            *(undefined4 *)(iVar4 + 4 + iVar3 * 4) = 0;
            *(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xfffffff7;
          }
          *(uint *)(iVar1 + 0x18) = *(uint *)(iVar1 + 0x18) & 0xffffffdf;
          *(undefined4 *)(iVar2 + 4) = 0;
        }
      }
      if ((int)((uint)*(byte *)(param_1 + 0x18) << 0x1b) < 0) {
        iVar1 = *(int *)(param_1 + 0x20);
      }
      else {
        FUN_005140c6(param_1);
        iVar1 = *(int *)(param_1 + 0x20);
        if (*(int *)(param_1 + 0x24) != 0) {
          FUN_00514178(param_1);
        }
      }
      param_1 = iVar1;
    } while (iVar1 != 0);
    return;
  }
  FUN_004b127c(0x2000);
  return;
}

