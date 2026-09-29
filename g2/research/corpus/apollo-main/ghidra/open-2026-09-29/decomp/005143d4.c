
void FUN_005143d4(int param_1,int param_2)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  piVar1 = DAT_00514b78;
  if (param_1 == 0) {
    uVar2 = 0x2000;
  }
  else {
    if ((*(byte *)(param_1 + 0xc) & 7) == 0) {
      if (*(int *)(param_1 + 0x24) != 0) {
        param_1 = *(int *)(param_1 + 0x24);
      }
      if (param_2 < 2) {
        param_2 = 2;
      }
      else if (2 < param_2) {
        iVar3 = *(int *)(param_1 + 0x10) << 2;
        iVar4 = iVar3 / param_2;
        if (iVar4 < 0x200) {
          if (param_2 << 0x1f < 0) {
            param_2 = param_2 + 1;
          }
          do {
            if (param_2 < 4) break;
            param_2 = param_2 + -2;
            iVar4 = iVar3 / param_2;
          } while (iVar4 < 0x200);
          if (iVar4 < 0x200) {
            uVar2 = 0x10000;
            goto LAB_0051443c;
          }
        }
      }
      iVar3 = *(int *)(param_1 + 0x10) * 4;
      if (iVar3 - param_2 * (iVar3 / param_2) == 0) {
        iVar4 = *DAT_00514b78;
        iVar3 = *(int *)(iVar4 + 4);
        if (iVar3 != 0) {
          iVar5 = *(int *)(iVar3 + 0x14);
          if (iVar5 + 2 <= *(int *)(iVar3 + 0x10)) {
            iVar6 = *(int *)(iVar3 + 8);
            *(undefined4 *)(iVar6 + iVar5 * 4) = 0x50000;
            *(undefined4 *)(iVar6 + 4 + iVar5 * 4) = 0;
            *(uint *)(iVar3 + 0x18) = *(uint *)(iVar3 + 0x18) & 0xfffffff7;
          }
          *(uint *)(iVar3 + 0x18) = *(uint *)(iVar3 + 0x18) & 0xffffffdf;
          *(undefined4 *)(iVar4 + 4) = 0;
        }
        if (param_1 == 0) {
          FUN_004b127c(0x2000);
        }
        else {
          *(uint *)(param_1 + 0x18) = *(uint *)(param_1 + 0x18) | 0x20;
        }
        *(undefined4 *)(param_1 + 0x34) = 0xffffffff;
        *(undefined4 *)(param_1 + 0x38) = 0xffffffff;
        iVar3 = *(int *)(param_1 + 0x10) / param_2;
        if (iVar3 << 0x1f < 0) {
          iVar3 = iVar3 + -1;
        }
        *(int *)(param_1 + 0x2c) = iVar3;
        *(int *)(param_1 + 0x28) = param_2;
        *(undefined4 *)(param_1 + 0x30) = 0;
        *(int *)(*piVar1 + 4) = param_1;
        return;
      }
    }
    uVar2 = 0x4000;
  }
LAB_0051443c:
  FUN_004b127c(uVar2);
  return;
}

