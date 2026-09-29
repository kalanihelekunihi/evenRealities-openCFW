
void FUN_005b0d24(int param_1,undefined1 param_2)

{
  byte bVar1;
  int iVar2;
  undefined1 uVar3;
  byte bVar4;
  
  bVar1 = FUN_005b0c30(param_2);
  for (bVar4 = 0; bVar4 < 4; bVar4 = bVar4 + 1) {
    if ((*(int *)(param_1 + (uint)bVar4 * 4 + 0x6c) != 0) &&
       (iVar2 = FUN_0043e2ea(*(undefined4 *)(param_1 + (uint)bVar4 * 4 + 0x6c)), iVar2 != 0)) {
      if (bVar4 < bVar1) {
        uVar3 = 0;
      }
      else {
        uVar3 = 0xff;
      }
      FUN_005b0c72(*(undefined4 *)(param_1 + (uint)bVar4 * 4 + 0x6c),uVar3);
    }
  }
  return;
}

