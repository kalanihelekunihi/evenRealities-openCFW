
int FT_Outline_Decompose(short *param_1,undefined4 *param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  uint uVar4;
  int *piVar5;
  int *piVar6;
  byte *pbVar7;
  byte *pbVar8;
  int iVar9;
  int iVar10;
  int local_70;
  int local_6c;
  int local_68;
  int local_64;
  int local_60;
  int local_5c;
  int local_58;
  int local_54;
  int local_50;
  int local_4c;
  int local_48;
  int local_44;
  int local_40;
  int local_3c;
  int local_38;
  int local_34;
  int local_30;
  short *local_28;
  
  if (param_1 == (short *)0x0) {
    iVar2 = 0x14;
  }
  else if (param_2 == (undefined4 *)0x0) {
    iVar2 = 6;
  }
  else {
    uVar4 = param_2[4];
    iVar2 = param_2[5];
    iVar10 = 0;
    iVar9 = 0;
    local_28 = param_1;
LAB_0052753e:
    if (iVar9 < *local_28) {
      local_68 = (int)*(short *)(*(int *)(local_28 + 6) + iVar9 * 2);
      if (-1 < local_68) {
        piVar5 = (int *)(*(int *)(local_28 + 2) + local_68 * 8);
        piVar3 = (int *)(*(int *)(local_28 + 2) + iVar10 * 8);
        local_64 = *piVar3;
        local_60 = piVar3[1];
        if (local_64 < 0) {
          local_64 = -(-local_64 << (uVar4 & 0xff));
        }
        else {
          local_64 = local_64 << (uVar4 & 0xff);
        }
        local_64 = local_64 - iVar2;
        if (local_60 < 0) {
          local_60 = -(-local_60 << (uVar4 & 0xff));
        }
        else {
          local_60 = local_60 << (uVar4 & 0xff);
        }
        local_60 = local_60 - iVar2;
        piVar3 = (int *)(*(int *)(local_28 + 2) + local_68 * 8);
        local_70 = *piVar3;
        local_6c = piVar3[1];
        if (local_70 < 0) {
          local_70 = -(-local_70 << (uVar4 & 0xff));
        }
        else {
          local_70 = local_70 << (uVar4 & 0xff);
        }
        local_70 = local_70 - iVar2;
        if (local_6c < 0) {
          local_6c = -(-local_6c << (uVar4 & 0xff));
        }
        else {
          local_6c = local_6c << (uVar4 & 0xff);
        }
        local_6c = local_6c - iVar2;
        piVar3 = (int *)(*(int *)(local_28 + 2) + iVar10 * 8);
        pbVar7 = (byte *)(*(int *)(local_28 + 4) + iVar10);
        if ((*pbVar7 & 3) != 2) {
          iVar10 = local_64;
          iVar1 = local_60;
          if ((*pbVar7 & 3) == 0) {
            if ((*(byte *)(*(int *)(local_28 + 4) + local_68) & 3) == 1) {
              piVar5 = piVar5 + -2;
            }
            else {
              local_70 = (local_70 + local_64) / 2;
              local_6c = (local_6c + local_60) / 2;
            }
            piVar3 = piVar3 + -2;
            pbVar7 = pbVar7 + -1;
            iVar10 = local_70;
            iVar1 = local_6c;
          }
          local_6c = iVar1;
          local_70 = iVar10;
          iVar10 = (*(code *)*param_2)(&local_70,param_3);
joined_r0x0052763a:
          if (iVar10 != 0) {
            return iVar10;
          }
          do {
            if (piVar5 <= piVar3) {
              iVar10 = (*(code *)param_2[1])(&local_70,param_3);
LAB_005278b6:
              if (iVar10 != 0) {
                return iVar10;
              }
              iVar10 = local_68 + 1;
              iVar9 = iVar9 + 1;
              goto LAB_0052753e;
            }
            piVar6 = piVar3 + 2;
            pbVar8 = pbVar7 + 1;
            if ((*pbVar8 & 3) == 0) {
              if (*piVar6 < 0) {
                local_64 = -(-*piVar6 << (uVar4 & 0xff));
              }
              else {
                local_64 = *piVar6 << (uVar4 & 0xff);
              }
              local_64 = local_64 - iVar2;
              if (piVar3[3] < 0) {
                local_60 = -(-piVar3[3] << (uVar4 & 0xff));
              }
              else {
                local_60 = piVar3[3] << (uVar4 & 0xff);
              }
              local_60 = local_60 - iVar2;
              while( true ) {
                if (piVar5 <= piVar6) {
                  iVar10 = (*(code *)param_2[2])(&local_64,&local_70,param_3);
                  goto LAB_005278b6;
                }
                piVar3 = piVar6 + 2;
                pbVar8 = pbVar8 + 1;
                if (*piVar3 < 0) {
                  local_5c = -(-*piVar3 << (uVar4 & 0xff));
                }
                else {
                  local_5c = *piVar3 << (uVar4 & 0xff);
                }
                local_5c = local_5c - iVar2;
                if (piVar6[3] < 0) {
                  local_58 = -(-piVar6[3] << (uVar4 & 0xff));
                }
                else {
                  local_58 = piVar6[3] << (uVar4 & 0xff);
                }
                local_58 = local_58 - iVar2;
                if ((*pbVar8 & 3) == 1) break;
                if ((*pbVar8 & 3) != 0) goto LAB_005275c8;
                local_3c = (local_5c + local_64) / 2;
                local_38 = (local_58 + local_60) / 2;
                iVar10 = (*(code *)param_2[2])(&local_64,&local_3c,param_3);
                if (iVar10 != 0) {
                  return iVar10;
                }
                local_64 = local_5c;
                local_60 = local_58;
                piVar6 = piVar3;
              }
              iVar10 = (*(code *)param_2[2])(&local_64,&local_5c,param_3);
              pbVar7 = pbVar8;
            }
            else {
              if ((*pbVar8 & 3) == 1) goto code_r0x00527680;
              if ((piVar5 < piVar3 + 4) || ((pbVar7[2] & 3) != 2)) break;
              piVar6 = piVar3 + 6;
              pbVar7 = pbVar7 + 3;
              if (piVar3[2] < 0) {
                local_4c = -(-piVar3[2] << (uVar4 & 0xff));
              }
              else {
                local_4c = piVar3[2] << (uVar4 & 0xff);
              }
              local_4c = local_4c - iVar2;
              if (piVar3[3] < 0) {
                local_48 = -(-piVar3[3] << (uVar4 & 0xff));
              }
              else {
                local_48 = piVar3[3] << (uVar4 & 0xff);
              }
              local_48 = local_48 - iVar2;
              if (piVar3[4] < 0) {
                local_54 = -(-piVar3[4] << (uVar4 & 0xff));
              }
              else {
                local_54 = piVar3[4] << (uVar4 & 0xff);
              }
              local_54 = local_54 - iVar2;
              if (piVar3[5] < 0) {
                local_50 = -(-piVar3[5] << (uVar4 & 0xff));
              }
              else {
                local_50 = piVar3[5] << (uVar4 & 0xff);
              }
              local_50 = local_50 - iVar2;
              if (piVar5 < piVar6) {
                iVar10 = (*(code *)param_2[3])(&local_4c,&local_54,&local_70,param_3);
                goto LAB_005278b6;
              }
              if (*piVar6 < 0) {
                local_44 = -(-*piVar6 << (uVar4 & 0xff));
              }
              else {
                local_44 = *piVar6 << (uVar4 & 0xff);
              }
              local_44 = local_44 - iVar2;
              if (piVar3[7] < 0) {
                local_40 = -(-piVar3[7] << (uVar4 & 0xff));
              }
              else {
                local_40 = piVar3[7] << (uVar4 & 0xff);
              }
              local_40 = local_40 - iVar2;
              iVar10 = (*(code *)param_2[3])(&local_4c,&local_54,&local_44,param_3);
              piVar3 = piVar6;
            }
            if (iVar10 != 0) {
              return iVar10;
            }
          } while( true );
        }
      }
LAB_005275c8:
      iVar2 = 0x14;
    }
    else {
      iVar2 = 0;
    }
  }
  return iVar2;
code_r0x00527680:
  if (*piVar6 < 0) {
    local_34 = -(-*piVar6 << (uVar4 & 0xff));
  }
  else {
    local_34 = *piVar6 << (uVar4 & 0xff);
  }
  local_34 = local_34 - iVar2;
  if (piVar3[3] < 0) {
    local_30 = -(-piVar3[3] << (uVar4 & 0xff));
  }
  else {
    local_30 = piVar3[3] << (uVar4 & 0xff);
  }
  local_30 = local_30 - iVar2;
  iVar10 = (*(code *)param_2[1])(&local_34,param_3);
  piVar3 = piVar6;
  pbVar7 = pbVar8;
  goto joined_r0x0052763a;
}

