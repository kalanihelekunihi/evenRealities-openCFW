
int FUN_005d0de0(int *param_1,int param_2,int param_3,uint param_4)

{
  char cVar1;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  int iVar9;
  uint uVar10;
  undefined4 *puVar11;
  uint local_68;
  byte local_64;
  int local_60;
  int local_5c;
  int local_58;
  uint local_54;
  uint local_50;
  char local_4c;
  int local_48;
  undefined1 auStack_44 [8];
  char local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  uint uStack_28;
  
  uStack_28 = param_4;
  FUN_005d0a72(param_1,&local_54);
  if (local_4c == '\0') {
LAB_005d0dfe:
    local_60 = 3;
  }
  else {
    uVar4 = 1;
    iVar6 = 0;
    local_68 = local_54;
    local_64 = *(byte *)(param_2 + 5);
    uVar5 = local_50;
    local_58 = param_2;
    local_48 = param_3;
    if (local_64 == 7) {
      iVar7 = *param_1;
      iVar9 = param_1[2];
      *param_1 = local_54 + 1;
      param_1[2] = local_50 - 1;
      FUN_005d0a72(param_1,auStack_44);
      *param_1 = iVar7;
      param_1[2] = iVar9;
      if (local_3c == '\x03') {
        local_64 = 8;
        uVar10 = uVar4;
LAB_005d0e64:
        uVar4 = uVar10;
        if (param_4 == 0) goto LAB_005d0dfe;
        iVar6 = 1;
        local_68 = local_68 + 1;
        uVar5 = local_50 - 1;
      }
    }
    else {
      uVar10 = param_4;
      if (local_4c == '\x03') goto LAB_005d0e64;
    }
    for (; uVar4 != 0; uVar4 = uVar4 - 1) {
      piVar8 = (int *)(*(int *)(local_48 + iVar6 * 4) + *(int *)(local_58 + 0xc));
      FUN_005d0736(&local_68,uVar5);
      if (local_64 == 1) {
        iVar7 = FUN_005d0d84(&local_68,uVar5);
LAB_005d0ea0:
        cVar1 = *(char *)(local_58 + 0x10);
        if (cVar1 == '\x01') {
          *(char *)piVar8 = (char)iVar7;
        }
        else if (cVar1 == '\x02') {
          *(short *)piVar8 = (short)iVar7;
        }
        else if (cVar1 == '\x04') {
          *piVar8 = iVar7;
        }
        else {
          *piVar8 = iVar7;
        }
      }
      else {
        if (local_64 == 0) goto LAB_005d0dfe;
        if (local_64 == 3) {
          iVar7 = FUN_005d01de(&local_68,uVar5,0);
          goto LAB_005d0ea0;
        }
        if (local_64 < 3) {
          iVar7 = FUN_005d018a(&local_68,uVar5);
          goto LAB_005d0ea0;
        }
        if (local_64 == 5) {
LAB_005d0f68:
          iVar7 = param_1[4];
          if (local_68 < uVar5) {
            if (local_4c == '\x04') {
              iVar9 = (uVar5 - local_68) + -1;
            }
            else {
              if (local_4c != '\x02') {
                return 3;
              }
              iVar9 = (uVar5 - local_68) + -2;
            }
            local_68 = local_68 + 1;
            if (*piVar8 != 0) {
              ft_mem_free(iVar7,*piVar8);
              *piVar8 = 0;
              *piVar8 = 0;
            }
            iVar7 = ft_mem_alloc(iVar7,iVar9 + 1,&local_60);
            if (local_60 != 0) {
              return local_60;
            }
            local_5c = iVar9;
            FUN_00439be4(iVar7,local_68,iVar9);
            *(undefined1 *)(iVar7 + iVar9) = 0;
            *piVar8 = iVar7;
          }
        }
        else {
          if (local_64 < 5) {
            iVar7 = FUN_005d01de(&local_68,uVar5,3);
            goto LAB_005d0ea0;
          }
          if (local_64 == 7) {
            iVar7 = FUN_005d0cc2(&local_68,uVar5,4,&local_38,0);
            if (iVar7 < 4) {
              return 3;
            }
            iVar7 = FT_RoundFix(local_38);
            *piVar8 = iVar7;
            iVar7 = FT_RoundFix(local_34);
            piVar8[1] = iVar7;
            iVar7 = FT_RoundFix(local_30);
            piVar8[2] = iVar7;
            iVar7 = FT_RoundFix(local_2c);
            piVar8[3] = iVar7;
          }
          else {
            if (local_64 < 7) goto LAB_005d0f68;
            if (local_64 != 8) goto LAB_005d0dfe;
            local_5c = param_1[4];
            iVar7 = ft_mem_realloc(local_5c,4,0,param_4 << 2,0,&local_60);
            if (local_60 != 0) {
              return local_60;
            }
            for (uVar10 = 0; uVar10 < 4; uVar10 = uVar10 + 1) {
              uVar3 = FUN_005d0cc2(&local_68,uVar5,param_4,iVar7 + param_4 * uVar10 * 4,0);
              if (((int)uVar3 < 0) || (uVar3 < param_4)) {
                local_60 = 3;
                ft_mem_free(local_5c,iVar7);
                return local_60;
              }
              FUN_005d0736(&local_68,uVar5);
            }
            for (uVar10 = 0; uVar10 < param_4; uVar10 = uVar10 + 1) {
              puVar11 = *(undefined4 **)(local_48 + uVar10 * 4);
              uVar2 = FT_RoundFix(*(undefined4 *)(iVar7 + uVar10 * 4));
              *puVar11 = uVar2;
              uVar2 = FT_RoundFix(*(undefined4 *)(iVar7 + (param_4 + uVar10) * 4));
              puVar11[1] = uVar2;
              uVar2 = FT_RoundFix(*(undefined4 *)(iVar7 + (uVar10 + param_4 * 2) * 4));
              puVar11[2] = uVar2;
              uVar2 = FT_RoundFix(*(undefined4 *)(iVar7 + (param_4 * 3 + uVar10) * 4));
              puVar11[3] = uVar2;
            }
            ft_mem_free(local_5c,iVar7);
          }
        }
      }
      iVar6 = iVar6 + 1;
    }
    local_60 = 0;
  }
  return local_60;
}

