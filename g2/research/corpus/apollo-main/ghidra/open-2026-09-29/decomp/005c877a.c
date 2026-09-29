
void FUN_005c877a(int param_1)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  
  if ((*(byte *)(param_1 + 0x70) & 7) >> 2 != 0) {
    FUN_004997f8(*(undefined4 *)(param_1 + 0x2c));
    uVar1 = (*(code *)*DAT_005c8d34)();
    if (uVar1 != 0) {
      uVar2 = FUN_005c81a8(param_1);
      iVar3 = FUN_00454768(uVar2);
      iVar4 = FUN_0044f718(iVar3 * uVar1 + 1);
      for (uVar5 = 0; uVar5 < uVar1; uVar5 = uVar5 + 1) {
        FUN_00454738(iVar3 * uVar5 + iVar4,uVar2,iVar3);
      }
      *(undefined1 *)(iVar4 + iVar3 * uVar5) = 0;
      FUN_0049942e(*(undefined4 *)(param_1 + 0x2c),iVar4);
      FUN_0044f758(iVar4);
      FUN_005c8fa8(param_1);
      FUN_005c88ec(param_1);
    }
  }
  return;
}

