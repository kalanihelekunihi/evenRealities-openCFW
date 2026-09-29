
void FUN_005e17c2(int param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int local_3c;
  int local_38;
  
  iVar7 = *(int *)(param_1 + 0xb8) >> 8;
  iVar1 = param_3 >> 8;
  if (((iVar7 < *(int *)(param_1 + 0x94)) || (iVar1 < *(int *)(param_1 + 0x94))) &&
     ((*(int *)(param_1 + 0x90) <= iVar7 || (*(int *)(param_1 + 0x90) <= iVar1)))) {
    iVar2 = *(int *)(param_1 + 0xb8) + iVar7 * -0x100;
    iVar3 = param_3 + iVar1 * -0x100;
    if (iVar7 == iVar1) {
      FUN_005e1686(param_1,iVar7,*(undefined4 *)(param_1 + 0xb4),iVar2,param_2,iVar3);
    }
    else {
      local_3c = param_2 - *(int *)(param_1 + 0xb4);
      iVar5 = param_3 - *(int *)(param_1 + 0xb8);
      if (local_3c == 0) {
        iVar4 = *(int *)(param_1 + 0xb4) >> 8;
        iVar6 = (*(int *)(param_1 + 0xb4) + iVar4 * -0x100) * 2;
        if (iVar5 < 1) {
          iVar5 = 0;
          iVar8 = -1;
        }
        else {
          iVar5 = 0x100;
          iVar8 = 1;
        }
        *(int *)(param_1 + 0x98) = (iVar5 - iVar2) * iVar6 + *(int *)(param_1 + 0x98);
        *(int *)(param_1 + 0x9c) = (iVar5 - iVar2) + *(int *)(param_1 + 0x9c);
        iVar7 = iVar8 + iVar7;
        FUN_005e1618(param_1,iVar4,iVar7);
        iVar9 = iVar5 * 2 + -0x100;
        iVar2 = iVar9 * iVar6;
        while (iVar7 != iVar1) {
          *(int *)(param_1 + 0x98) = iVar2 + *(int *)(param_1 + 0x98);
          *(int *)(param_1 + 0x9c) = iVar9 + *(int *)(param_1 + 0x9c);
          iVar7 = iVar8 + iVar7;
          FUN_005e1618(param_1,iVar4,iVar7);
        }
        iVar7 = iVar5 + iVar3 + -0x100;
        *(int *)(param_1 + 0x98) = iVar7 * iVar6 + *(int *)(param_1 + 0x98);
        *(int *)(param_1 + 0x9c) = iVar7 + *(int *)(param_1 + 0x9c);
      }
      else {
        if (iVar5 < 1) {
          iVar6 = 0;
          local_38 = -1;
          iVar5 = -iVar5;
          iVar4 = iVar2;
        }
        else {
          iVar6 = 0x100;
          local_38 = 1;
          iVar4 = 0x100 - iVar2;
        }
        iVar4 = local_3c * iVar4;
        iVar8 = iVar4 / iVar5;
        iVar4 = iVar4 - iVar5 * (iVar4 / iVar5);
        if (iVar4 < 0) {
          iVar8 = iVar8 + -1;
          iVar4 = iVar5 + iVar4;
        }
        iVar8 = iVar8 + *(int *)(param_1 + 0xb4);
        FUN_005e1686(param_1,iVar7,*(undefined4 *)(param_1 + 0xb4),iVar2,iVar8,iVar6);
        iVar7 = local_38 + iVar7;
        FUN_005e1618(param_1,iVar8 >> 8,iVar7);
        if (iVar7 != iVar1) {
          local_3c = local_3c * 0x100;
          iVar9 = local_3c / iVar5;
          local_3c = local_3c - iVar5 * (local_3c / iVar5);
          iVar2 = iVar8;
          if (local_3c < 0) {
            iVar9 = iVar9 + -1;
            local_3c = iVar5 + local_3c;
          }
          do {
            iVar4 = local_3c + iVar4;
            iVar8 = iVar9;
            if (iVar5 <= iVar4) {
              iVar4 = iVar4 - iVar5;
              iVar8 = iVar9 + 1;
            }
            iVar8 = iVar8 + iVar2;
            FUN_005e1686(param_1,iVar7,iVar2,0x100 - iVar6,iVar8,iVar6);
            iVar7 = local_38 + iVar7;
            FUN_005e1618(param_1,iVar8 >> 8,iVar7);
            iVar2 = iVar8;
          } while (iVar7 != iVar1);
        }
        FUN_005e1686(param_1,iVar7,iVar8,0x100 - iVar6,param_2,iVar3);
      }
    }
  }
  *(int *)(param_1 + 0xb4) = param_2;
  *(int *)(param_1 + 0xb8) = param_3;
  return;
}

