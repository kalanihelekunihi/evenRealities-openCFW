
void FUN_0045383c(void)

{
  int iVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 in_r3;
  int iVar8;
  ushort uVar9;
  char cVar10;
  undefined4 local_80;
  undefined1 auStack_78 [8];
  int local_70;
  int local_6c;
  undefined1 auStack_68 [64];
  undefined4 uStack_28;
  
  iVar1 = DAT_00454168;
  if (((*(char *)(*(int *)(DAT_00454168 + 0x10) + 0x39) == '\x01') &&
      (uStack_28 = in_r3, iVar3 = FUN_0044fc52(*(undefined4 *)(DAT_00454168 + 0x10)), iVar3 != 0))
     && (iVar3 = FUN_00482d88(*(int *)(iVar1 + 0x10) + 0x268), iVar3 == 0)) {
    FUN_00454692(*(undefined4 *)(iVar1 + 0x10));
    uVar4 = *(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x24);
    if (*(int *)(*(int *)(iVar1 + 0x10) + 0x24) == *(int *)(*(int *)(iVar1 + 0x10) + 0x1c)) {
      local_80 = *(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x20);
    }
    else {
      local_80 = *(undefined4 *)(*(int *)(iVar1 + 0x10) + 0x1c);
    }
    iVar3 = FUN_0044fa7e(*(undefined4 *)(iVar1 + 0x10));
    iVar5 = FUN_0044faa8(*(undefined4 *)(iVar1 + 0x10));
    FUN_0043bb00(auStack_68,0,0x40);
    for (uVar9 = 0; (uint)uVar9 < *(uint *)(*(int *)(iVar1 + 0x10) + 0x260); uVar9 = uVar9 + 1) {
      if (*(char *)(*(int *)(iVar1 + 0x10) + (uint)uVar9 + 0x240) == '\0') {
        iVar6 = FUN_00482cd8(*(int *)(iVar1 + 0x10) + 0x268);
        while (iVar8 = iVar6, iVar8 != 0) {
          iVar6 = FUN_00482cf0(*(int *)(iVar1 + 0x10) + 0x268,iVar8);
          cVar2 = FUN_00450c2a(auStack_68,iVar8,*(int *)(iVar1 + 0x10) + (uint)uVar9 * 0x10 + 0x40);
          if (cVar2 != -1) {
            for (cVar10 = '\0'; cVar10 < cVar2; cVar10 = cVar10 + '\x01') {
              uVar7 = FUN_00482b56(*(int *)(iVar1 + 0x10) + 0x268,iVar8);
              FUN_00439c04(uVar7,auStack_68 + cVar10 * 0x10,0x10);
            }
            FUN_00482c0e(*(int *)(iVar1 + 0x10) + 0x268,iVar8);
            FUN_0044f758(iVar8);
          }
        }
      }
    }
    FUN_0048949c(auStack_78,0x10);
    local_70 = iVar3 + -1;
    local_6c = iVar5 + -1;
    for (iVar3 = FUN_00482cd8(*(int *)(iVar1 + 0x10) + 0x268); iVar3 != 0;
        iVar3 = FUN_00482cf0(*(int *)(iVar1 + 0x10) + 0x268,iVar3)) {
      FUN_00450bcc(iVar3,iVar3,auStack_78);
      FUN_0048ad42(uVar4,iVar3,local_80,iVar3);
    }
    FUN_00482da4(*(int *)(iVar1 + 0x10) + 0x268);
  }
  return;
}

