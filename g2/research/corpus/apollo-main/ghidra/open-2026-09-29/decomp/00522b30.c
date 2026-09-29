
void FUN_00522b30(uint param_1,int param_2,int param_3,int param_4,int param_5)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  
  if (param_3 / 2 < param_5) {
    param_5 = param_3 / 2;
  }
  if (param_4 / 2 < param_5) {
    param_5 = param_4 / 2;
  }
  if (param_5 < 1) {
    iVar3 = param_3;
    if (0 < param_3) {
      iVar3 = param_4;
    }
    if ((0 < iVar3) && (puVar2 = (undefined4 *)FUN_00514aec(3), puVar2 != (undefined4 *)0x0)) {
      *puVar2 = 0x104;
      puVar2[1] = param_1 & 0xffff | param_2 << 0x10;
      puVar2[2] = 0x108;
      puVar2[3] = param_1 + param_3 & 0xffff | (param_2 + param_4) * 0x10000;
      puVar2[4] = DAT_005232cc;
      puVar2[5] = *(uint *)(*DAT_00522f18 + 0x18) | 2;
      return;
    }
  }
  else {
    iVar3 = 0;
    iVar7 = param_5 * -2 + 3;
    iVar9 = param_4 + param_5 * -2;
    if (iVar9 < 1) {
      iVar4 = 0;
    }
    else {
      iVar4 = 3;
    }
    iVar5 = param_5;
    iVar8 = iVar7;
    while( true ) {
      if (iVar8 < 0) {
        iVar8 = iVar8 + iVar3 * 4 + 6;
      }
      else {
        if (iVar3 != iVar5) {
          iVar4 = iVar4 + 6;
        }
        iVar8 = iVar8 + (iVar3 - iVar5) * 4 + 10;
        iVar5 = iVar5 + -1;
      }
      iVar3 = iVar3 + 1;
      if (iVar5 < iVar3) break;
      if (iVar3 != 0) {
        iVar4 = iVar4 + 6;
      }
    }
    iVar3 = FUN_00514d2c(iVar4);
    if (-1 < iVar3) {
      iVar4 = param_5 + param_1;
      iVar3 = param_5 + param_2;
      iVar8 = ((param_2 + param_4) - param_5) + -1;
      iVar5 = ((param_3 + param_1) - param_5) + -1;
      if (iVar9 >= 1) {
        iVar6 = param_3;
        if (0 < param_3) {
          iVar6 = iVar9;
        }
        if ((0 < iVar6) && (puVar2 = (undefined4 *)FUN_00514aec(3), puVar2 != (undefined4 *)0x0)) {
          *puVar2 = 0x104;
          puVar2[1] = param_1 & 0xffff | iVar3 * 0x10000;
          puVar2[2] = 0x108;
          puVar2[3] = param_3 + param_1 & 0xffff | (iVar9 + iVar3) * 0x10000;
          puVar2[4] = DAT_005232cc;
          puVar2[5] = *(uint *)(*DAT_00522f18 + 0x18) | 2;
        }
      }
      iVar9 = 0;
      while( true ) {
        if (iVar7 < 0) {
          iVar7 = iVar7 + iVar9 * 4 + 6;
        }
        else {
          if (iVar9 != param_5) {
            puVar2 = (undefined4 *)FUN_00514aec(3);
            if (puVar2 != (undefined4 *)0x0) {
              *puVar2 = 0x104;
              puVar2[2] = 0x108;
              puVar2[1] = iVar4 - iVar9 & 0xffffU | (iVar3 - param_5) * 0x10000;
              piVar1 = DAT_00522f18;
              puVar2[3] = iVar9 + iVar5 & 0xffffU | (iVar3 - param_5) * 0x10000;
              puVar2[4] = DAT_005232cc;
              puVar2[5] = *(uint *)(*piVar1 + 0x18) | 1;
            }
            puVar2 = (undefined4 *)FUN_00514aec(3);
            if (puVar2 != (undefined4 *)0x0) {
              *puVar2 = 0x104;
              iVar6 = param_5 + iVar8;
              puVar2[2] = 0x108;
              puVar2[1] = iVar4 - iVar9 & 0xffffU | iVar6 * 0x10000;
              piVar1 = DAT_00522f18;
              puVar2[3] = iVar9 + iVar5 & 0xffffU | iVar6 * 0x10000;
              puVar2[4] = DAT_005232cc;
              puVar2[5] = *(uint *)(*piVar1 + 0x18) | 1;
            }
          }
          iVar7 = iVar7 + (iVar9 - param_5) * 4 + 10;
          param_5 = param_5 + -1;
        }
        iVar9 = iVar9 + 1;
        if (param_5 < iVar9) break;
        if (iVar9 != 0) {
          puVar2 = (undefined4 *)FUN_00514aec(3);
          if (puVar2 != (undefined4 *)0x0) {
            *puVar2 = 0x104;
            puVar2[2] = 0x108;
            puVar2[1] = iVar4 - param_5 & 0xffffU | (iVar3 - iVar9) * 0x10000;
            piVar1 = DAT_00522f18;
            puVar2[3] = param_5 + iVar5 & 0xffffU | (iVar3 - iVar9) * 0x10000;
            puVar2[4] = DAT_005232cc;
            puVar2[5] = *(uint *)(*piVar1 + 0x18) | 1;
          }
          puVar2 = (undefined4 *)FUN_00514aec(3);
          if (puVar2 != (undefined4 *)0x0) {
            *puVar2 = 0x104;
            iVar6 = iVar9 + iVar8;
            puVar2[2] = 0x108;
            puVar2[1] = iVar4 - param_5 & 0xffffU | iVar6 * 0x10000;
            piVar1 = DAT_00522f18;
            puVar2[3] = param_5 + iVar5 & 0xffffU | iVar6 * 0x10000;
            puVar2[4] = DAT_005232cc;
            puVar2[5] = *(uint *)(*piVar1 + 0x18) | 1;
          }
        }
      }
    }
  }
  return;
}

