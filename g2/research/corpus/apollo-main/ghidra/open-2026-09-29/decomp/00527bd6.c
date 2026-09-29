
undefined4 FT_Outline_EmboldenXY(short *param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
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
    uVar1 = 0x14;
  }
  else {
    local_40 = param_2 / 2;
    local_44 = param_3 / 2;
    if (local_40 == 0 && local_44 == 0) {
      uVar1 = 0;
    }
    else {
      local_28 = param_1;
      local_3c = FT_Outline_Get_Orientation(param_1);
      if (local_3c == 2) {
        if (*local_28 == 0) {
          uVar1 = 0;
        }
        else {
          uVar1 = 6;
        }
      }
      else {
        iVar9 = *(int *)(local_28 + 2);
        local_4c = 0;
        for (local_48 = 0; local_48 < *local_28; local_48 = local_48 + 1) {
          local_38 = 0;
          local_50 = (int)*(short *)(*(int *)(local_28 + 6) + local_48 * 2);
          local_30 = 0;
          local_34 = 0;
          local_58 = -1;
          iVar7 = 0;
          iVar6 = 0;
          iVar5 = 0;
          iVar10 = local_50;
          iVar2 = local_4c;
          while ((iVar12 = iVar2, iVar12 != iVar10 && (iVar10 != local_58))) {
            if (iVar12 == local_58) {
              local_60 = local_34;
              local_5c = local_30;
              iVar2 = local_38;
LAB_00527cc2:
              iVar8 = iVar2;
              iVar3 = local_60;
              iVar4 = local_5c;
              iVar11 = iVar12;
              if (iVar7 != 0) {
                if (local_58 < 0) {
                  local_58 = iVar10;
                  local_38 = iVar7;
                  local_34 = iVar6;
                  local_30 = iVar5;
                }
                iVar3 = FT_MulFix(iVar6,local_60);
                iVar4 = FT_MulFix(iVar5,local_5c);
                if (iVar4 + iVar3 < DAT_005286f8) {
                  local_64 = 0;
                  local_68 = 0;
                }
                else {
                  local_54 = iVar4 + iVar3 + 0x10000;
                  local_68 = local_5c + iVar5;
                  local_64 = local_60 + iVar6;
                  if (local_3c == 0) {
                    local_68 = -local_68;
                  }
                  else {
                    local_64 = -local_64;
                  }
                  iVar5 = FT_MulFix(local_60,iVar5);
                  iVar6 = FT_MulFix(local_5c,iVar6);
                  iVar5 = iVar5 - iVar6;
                  if (local_3c == 0) {
                    iVar5 = -iVar5;
                  }
                  if (iVar2 <= iVar7) {
                    iVar7 = iVar2;
                  }
                  iVar6 = FT_MulFix(iVar7,local_54);
                  iVar2 = FT_MulFix(local_40,iVar5);
                  if (iVar6 < iVar2) {
                    local_68 = FT_MulDiv(local_68,iVar7,iVar5);
                  }
                  else {
                    local_68 = FT_MulDiv(local_68,local_40,local_54);
                  }
                  iVar6 = FT_MulFix(iVar7,local_54);
                  iVar2 = FT_MulFix(local_44,iVar5);
                  if (iVar6 < iVar2) {
                    local_64 = FT_MulDiv(local_64,iVar7,iVar5);
                  }
                  else {
                    local_64 = FT_MulDiv(local_64,local_44,local_54);
                  }
                }
                while (iVar11 = iVar10, iVar3 = local_60, iVar4 = local_5c, iVar11 != iVar12) {
                  *(int *)(iVar9 + iVar11 * 8) = local_68 + local_40 + *(int *)(iVar9 + iVar11 * 8);
                  *(int *)(iVar9 + iVar11 * 8 + 4) =
                       local_64 + local_44 + *(int *)(iVar9 + iVar11 * 8 + 4);
                  iVar10 = local_4c;
                  if (iVar11 < local_50) {
                    iVar10 = iVar11 + 1;
                  }
                }
              }
            }
            else {
              local_60 = *(int *)(iVar9 + iVar12 * 8) - *(int *)(iVar9 + iVar10 * 8);
              local_5c = *(int *)(iVar9 + iVar12 * 8 + 4) - *(int *)(iVar9 + iVar10 * 8 + 4);
              iVar2 = FT_Vector_NormLen(&local_60);
              iVar8 = iVar7;
              iVar3 = iVar6;
              iVar4 = iVar5;
              iVar11 = iVar10;
              if (iVar2 != 0) goto LAB_00527cc2;
            }
            iVar7 = iVar8;
            iVar6 = iVar3;
            iVar5 = iVar4;
            iVar10 = iVar11;
            iVar2 = local_4c;
            if (iVar12 < local_50) {
              iVar2 = iVar12 + 1;
            }
          }
          local_4c = local_50 + 1;
        }
        uVar1 = 0;
      }
    }
  }
  return uVar1;
}

