
int cff_blend_build_vector(undefined1 *param_1,uint param_2,uint param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int *piVar4;
  int *piVar5;
  uint uVar6;
  uint uVar7;
  int local_38;
  uint *local_34;
  int *local_30;
  undefined4 local_2c;
  int iStack_28;
  
  local_38 = 0;
  local_2c = *(undefined4 *)(*(int *)(param_1 + 4) + 8);
  *param_1 = 0;
  iVar1 = *(int *)(param_1 + 4);
  local_34 = (uint *)(iVar1 + 0xc28);
  if ((param_3 == 0) || (param_3 == *(ushort *)(iVar1 + 0xc30))) {
    if (param_2 < *local_34) {
      local_30 = (int *)(*(int *)(iVar1 + 0xc2c) + param_2 * 8);
      uVar7 = *local_30 + 1;
      iStack_28 = param_4;
      uVar2 = ft_mem_realloc(local_2c,1,*(int *)(param_1 + 0x14) << 2,uVar7 * 4,
                             *(undefined4 *)(param_1 + 0x18),&local_38);
      *(undefined4 *)(param_1 + 0x18) = uVar2;
      if (local_38 == 0) {
        *(uint *)(param_1 + 0x14) = uVar7;
        for (uVar6 = 0; uVar6 < uVar7; uVar6 = uVar6 + 1) {
          if (uVar6 == 0) {
            **(undefined4 **)(param_1 + 0x18) = 0x10000;
          }
          else {
            uVar3 = *(uint *)(local_30[1] + uVar6 * 4 + -4);
            piVar4 = (int *)(local_34[4] + uVar3 * 4);
            if (local_34[3] <= uVar3) {
              return 3;
            }
            if (param_3 == 0) {
              *(undefined4 *)(*(int *)(param_1 + 0x18) + uVar6 * 4) = 0;
            }
            else {
              *(undefined4 *)(*(int *)(param_1 + 0x18) + uVar6 * 4) = 0x10000;
              for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1) {
                piVar5 = (int *)(*piVar4 + uVar3 * 0xc);
                uVar2 = 0x10000;
                if ((*piVar5 <= piVar5[1]) && (piVar5[1] <= piVar5[2])) {
                  if ((*piVar5 < 0) && ((0 < piVar5[2] && (piVar5[1] != 0)))) {
                    uVar2 = 0x10000;
                  }
                  else if (piVar5[1] == 0) {
                    uVar2 = 0x10000;
                  }
                  else if ((*(int *)(param_4 + uVar3 * 4) < *piVar5) ||
                          (piVar5[2] < *(int *)(param_4 + uVar3 * 4))) {
                    uVar2 = 0;
                  }
                  else if (*(int *)(param_4 + uVar3 * 4) == piVar5[1]) {
                    uVar2 = 0x10000;
                  }
                  else if (*(int *)(param_4 + uVar3 * 4) < piVar5[1]) {
                    uVar2 = FT_DivFix(*(int *)(param_4 + uVar3 * 4) - *piVar5,piVar5[1] - *piVar5);
                  }
                  else {
                    uVar2 = FT_DivFix(piVar5[2] - *(int *)(param_4 + uVar3 * 4),
                                      piVar5[2] - piVar5[1]);
                  }
                }
                uVar2 = FT_MulFix(*(undefined4 *)(*(int *)(param_1 + 0x18) + uVar6 * 4),uVar2);
                *(undefined4 *)(*(int *)(param_1 + 0x18) + uVar6 * 4) = uVar2;
              }
            }
          }
        }
        *(uint *)(param_1 + 8) = param_2;
        if (param_3 != 0) {
          uVar2 = ft_mem_realloc(local_2c,1,*(int *)(param_1 + 0xc) << 2,param_3 << 2,
                                 *(undefined4 *)(param_1 + 0x10),&local_38);
          *(undefined4 *)(param_1 + 0x10) = uVar2;
          if (local_38 != 0) {
            return local_38;
          }
          FUN_00439be4(*(undefined4 *)(param_1 + 0x10),param_4,param_3 << 2);
        }
        *(uint *)(param_1 + 0xc) = param_3;
        *param_1 = 1;
      }
    }
    else {
      local_38 = 3;
    }
  }
  else {
    local_38 = 3;
  }
  return local_38;
}

