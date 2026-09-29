
int FUN_00569748(int param_1,short *param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  int *piVar6;
  uint uVar7;
  byte *pbVar8;
  byte *pbVar9;
  uint uVar10;
  int local_68;
  int local_64;
  int local_60;
  int local_5c;
  int local_58;
  int local_54;
  int local_50;
  int local_4c;
  int local_48;
  int iStack_44;
  int local_40;
  int iStack_3c;
  int local_38;
  int local_34;
  int local_30;
  int iStack_2c;
  undefined4 uStack_28;
  
  if (param_2 == (short *)0x0) {
    iVar2 = 0x14;
  }
  else if (param_1 == 0) {
    iVar2 = 6;
  }
  else {
    uStack_28 = param_4;
    FUN_0056882a(param_1);
    uVar7 = 0;
    for (iVar2 = 0; iVar2 < *param_2; iVar2 = iVar2 + 1) {
      uVar10 = (uint)*(short *)(*(int *)(param_2 + 6) + iVar2 * 2);
      piVar6 = (int *)(*(int *)(param_2 + 2) + uVar10 * 8);
      if (uVar7 < uVar10) {
        piVar4 = (int *)(*(int *)(param_2 + 2) + uVar7 * 8);
        local_60 = *piVar4;
        local_5c = piVar4[1];
        piVar4 = (int *)(*(int *)(param_2 + 2) + uVar10 * 8);
        local_68 = *piVar4;
        local_64 = piVar4[1];
        piVar4 = (int *)(*(int *)(param_2 + 2) + uVar7 * 8);
        pbVar8 = (byte *)(uVar7 + *(int *)(param_2 + 4));
        if ((*pbVar8 & 3) == 2) {
          return 0x14;
        }
        iVar3 = local_60;
        iVar1 = local_5c;
        if ((*pbVar8 & 3) == 0) {
          if ((*(byte *)(*(int *)(param_2 + 4) + uVar10) & 3) == 1) {
            piVar6 = piVar6 + -2;
          }
          else {
            local_68 = (local_68 + local_60) / 2;
            local_64 = (local_64 + local_5c) / 2;
          }
          piVar4 = piVar4 + -2;
          pbVar8 = pbVar8 + -1;
          iVar3 = local_68;
          iVar1 = local_64;
        }
        local_64 = iVar1;
        local_68 = iVar3;
        iVar3 = FUN_005694e0(param_1,&local_68,param_3);
joined_r0x0056981a:
        do {
          piVar5 = piVar4;
          if (iVar3 != 0) {
            return iVar3;
          }
          while( true ) {
            iVar3 = 0;
            if (piVar6 <= piVar5) goto LAB_00569946;
            piVar4 = piVar5 + 2;
            pbVar9 = pbVar8 + 1;
            if ((*pbVar9 & 3) == 0) {
              local_60 = *piVar4;
              local_5c = piVar5[3];
              piVar5 = piVar4;
              goto LAB_005698b0;
            }
            if ((*pbVar9 & 3) == 1) break;
            if (piVar6 < piVar5 + 4) {
              return 0x14;
            }
            if ((pbVar8[2] & 3) != 2) {
              return 0x14;
            }
            piVar4 = piVar5 + 6;
            pbVar8 = pbVar8 + 3;
            local_40 = piVar5[2];
            iStack_3c = piVar5[3];
            local_48 = piVar5[4];
            iStack_44 = piVar5[5];
            if (piVar6 < piVar4) {
              iVar3 = FUN_00569160(param_1,&local_40,&local_48,&local_68);
              goto LAB_00569946;
            }
            local_30 = *piVar4;
            iStack_2c = piVar5[7];
            iVar3 = FUN_00569160(param_1,&local_40,&local_48,&local_30);
            piVar5 = piVar4;
            if (iVar3 != 0) {
              return iVar3;
            }
          }
          local_50 = *piVar4;
          local_4c = piVar5[3];
          iVar3 = FUN_00568d86(param_1,&local_50);
          pbVar8 = pbVar9;
        } while( true );
      }
LAB_0056978a:
      uVar7 = uVar10 + 1;
    }
    iVar2 = 0;
  }
  return iVar2;
LAB_005698b0:
  if (piVar6 <= piVar5) {
    iVar3 = FUN_00568e52(param_1,&local_60,&local_68);
LAB_00569946:
    if (iVar3 != 0) {
      return iVar3;
    }
    if ((*(char *)(param_1 + 0x14) == '\0') && (iVar3 = FUN_005695f8(param_1), iVar3 != 0)) {
      return iVar3;
    }
    goto LAB_0056978a;
  }
  piVar4 = piVar5 + 2;
  pbVar9 = pbVar9 + 1;
  local_58 = *piVar4;
  local_54 = piVar5[3];
  if ((*pbVar9 & 3) != 1) goto LAB_0056987a;
  iVar3 = FUN_00568e52(param_1,&local_60,&local_58);
  pbVar8 = pbVar9;
  goto joined_r0x0056981a;
LAB_0056987a:
  if ((*pbVar9 & 3) != 0) {
    return 0x14;
  }
  local_38 = (local_58 + local_60) / 2;
  local_34 = (local_54 + local_5c) / 2;
  iVar3 = FUN_00568e52(param_1,&local_60,&local_38);
  if (iVar3 != 0) {
    return iVar3;
  }
  local_60 = local_58;
  local_5c = local_54;
  piVar5 = piVar4;
  goto LAB_005698b0;
}

