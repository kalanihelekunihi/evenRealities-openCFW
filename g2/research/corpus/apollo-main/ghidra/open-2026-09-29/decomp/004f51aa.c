
undefined4 FUN_004f51aa(int param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iStack_ac;
  undefined1 auStack_a8 [44];
  int iStack_7c;
  undefined1 auStack_78 [44];
  int iStack_4c;
  undefined1 auStack_48 [48];
  
  iVar4 = *(int *)(param_1 + 0xc) + 2000;
  iVar1 = *(int *)(param_2 + 0xc) + 2000;
  if (iVar4 == iVar1) {
    if ((*(int *)(param_1 + 0x10) == *(int *)(param_2 + 0x10)) &&
       (*(int *)(param_1 + 0x14) == *(int *)(param_2 + 0x14))) {
      uVar2 = 0;
    }
    else if ((*(int *)(param_1 + 0x10) == *(int *)(param_2 + 0x10)) &&
            (*(int *)(param_2 + 0x14) == *(int *)(param_1 + 0x14) + 1)) {
      uVar2 = 1;
    }
    else {
      if ((*(int *)(param_2 + 0x10) == *(int *)(param_1 + 0x10) + 1) &&
         (*(int *)(param_2 + 0x14) == 1)) {
        FUN_00439c04(auStack_78,DAT_004f5c48,0x30);
        iVar1 = (&iStack_7c)[*(int *)(param_1 + 0x10)];
        if ((*(int *)(param_1 + 0x10) == 2) && (iVar3 = FUN_004f517c(iVar4), iVar3 != 0)) {
          iVar1 = 0x1d;
        }
        if (*(int *)(param_1 + 0x14) == iVar1) {
          return 1;
        }
      }
      if ((*(int *)(param_1 + 0x10) == *(int *)(param_2 + 0x10)) &&
         (*(int *)(param_2 + 0x14) == *(int *)(param_1 + 0x14) + -1)) {
        uVar2 = 2;
      }
      else {
        if ((*(int *)(param_2 + 0x10) == *(int *)(param_1 + 0x10) + -1) &&
           (*(int *)(param_1 + 0x14) == 1)) {
          FUN_00439c04(auStack_a8,DAT_004f5e14,0x30);
          iVar1 = (&iStack_ac)[*(int *)(param_2 + 0x10)];
          if ((*(int *)(param_2 + 0x10) == 2) && (iVar3 = FUN_004f517c(iVar4), iVar3 != 0)) {
            iVar1 = 0x1d;
          }
          if (*(int *)(param_2 + 0x14) == iVar1) {
            return 2;
          }
        }
        iVar1 = 0;
        if (*(int *)(param_1 + 0x10) == *(int *)(param_2 + 0x10)) {
          iVar1 = *(int *)(param_2 + 0x14) - *(int *)(param_1 + 0x14);
        }
        else {
          FUN_00439c04(auStack_48,DAT_004f5e7c,0x30);
          if (*(uint *)(param_1 + 0x10) < *(uint *)(param_2 + 0x10)) {
            for (uVar5 = *(uint *)(param_1 + 0x10); uVar5 < *(uint *)(param_2 + 0x10);
                uVar5 = uVar5 + 1) {
              iVar1 = (&iStack_4c)[uVar5] + iVar1;
              if ((uVar5 == 2) && (iVar3 = FUN_004f517c(iVar4), iVar3 != 0)) {
                iVar1 = iVar1 + 1;
              }
            }
            iVar1 = (*(int *)(param_2 + 0x14) + iVar1) - *(int *)(param_1 + 0x14);
          }
          else {
            for (uVar5 = *(uint *)(param_2 + 0x10); uVar5 < *(uint *)(param_1 + 0x10);
                uVar5 = uVar5 + 1) {
              iVar1 = (&iStack_4c)[uVar5] + iVar1;
              if ((uVar5 == 2) && (iVar3 = FUN_004f517c(iVar4), iVar3 != 0)) {
                iVar1 = iVar1 + 1;
              }
            }
            iVar1 = -((*(int *)(param_1 + 0x14) + iVar1) - *(int *)(param_2 + 0x14));
          }
        }
        if (iVar1 - 2U < 6) {
          uVar2 = 3;
        }
        else if (iVar1 + 7U < 6) {
          uVar2 = 4;
        }
        else {
          uVar2 = 5;
        }
      }
    }
  }
  else if ((((iVar1 == *(int *)(param_1 + 0xc) + 0x7d1) && (*(int *)(param_1 + 0x10) == 0xc)) &&
           (*(int *)(param_1 + 0x14) == 0x1f)) &&
          ((*(int *)(param_2 + 0x10) == 1 && (*(int *)(param_2 + 0x14) == 1)))) {
    uVar2 = 1;
  }
  else {
    uVar2 = 6;
  }
  return uVar2;
}

