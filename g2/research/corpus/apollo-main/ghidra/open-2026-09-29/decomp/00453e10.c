
void FUN_00453e10(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 auStack_28 [16];
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FUN_0048471a(param_1);
  iVar1 = DAT_00454168;
  iVar2 = FUN_0044fc52(*(undefined4 *)(DAT_00454168 + 0x10));
  if (iVar2 == 0) {
    FUN_00454692(*(undefined4 *)(iVar1 + 0x10));
  }
  iVar2 = FUN_00440fc4(*(undefined1 *)(*(int *)(iVar1 + 0x10) + 0x3c));
  if (iVar2 != 0) {
    FUN_00439c04(auStack_28,param_1 + 6,0x10);
    FUN_00450bb2(auStack_28,-param_1[1],-param_1[2]);
    FUN_0048ac40(*param_1,auStack_28);
  }
  iVar4 = 0;
  uVar3 = FUN_0044fc62(*(undefined4 *)(iVar1 + 0x10));
  iVar2 = FUN_00453f2e(param_1 + 6,uVar3);
  if (*(int *)(*(int *)(iVar1 + 0x10) + 0x2cc) != 0) {
    iVar4 = FUN_00453f2e(param_1 + 6,*(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x2cc));
  }
  if ((iVar2 == 0) && (iVar4 == 0)) {
    uVar3 = FUN_0044fd38(*(undefined4 *)(iVar1 + 0x10));
    FUN_00453fce(param_1,uVar3);
  }
  if ((int)((uint)*(byte *)(*(int *)(iVar1 + 0x10) + 0x2d8) << 0x1f) < 0) {
    if (iVar2 == 0) {
      iVar2 = *(int *)(*(int *)(iVar1 + 0x10) + 0x2c4);
    }
    FUN_00453fce(param_1,iVar2);
    if (*(int *)(*(int *)(iVar1 + 0x10) + 0x2cc) != 0) {
      if (iVar4 == 0) {
        iVar4 = *(int *)(*(int *)(iVar1 + 0x10) + 0x2cc);
      }
      FUN_00453fce(param_1,iVar4);
    }
  }
  else {
    if (*(int *)(*(int *)(iVar1 + 0x10) + 0x2cc) != 0) {
      if (iVar4 == 0) {
        iVar4 = *(int *)(*(int *)(iVar1 + 0x10) + 0x2cc);
      }
      FUN_00453fce(param_1,iVar4);
    }
    if (iVar2 == 0) {
      iVar2 = *(int *)(*(int *)(iVar1 + 0x10) + 0x2c4);
    }
    FUN_00453fce(param_1,iVar2);
  }
  uVar3 = FUN_0044fcbe(*(undefined4 *)(iVar1 + 0x10));
  FUN_00453fce(param_1,uVar3);
  uVar3 = FUN_0044fcfc(*(undefined4 *)(iVar1 + 0x10));
  FUN_00453fce(param_1,uVar3);
  return;
}

