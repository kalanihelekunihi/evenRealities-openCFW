
int tt_set_mm_blend(int param_1,uint param_2,int param_3,char param_4)

{
  bool bVar1;
  bool bVar2;
  uint uVar3;
  int *piVar4;
  int *piVar5;
  uint *puVar6;
  uint *puVar7;
  byte bVar8;
  uint uVar9;
  int local_30;
  undefined4 local_2c;
  int local_28;
  
  local_30 = 0;
  bVar2 = false;
  local_2c = *(undefined4 *)(param_1 + 100);
  *(undefined1 *)(param_1 + 0x2b9) = 0;
  if ((*(int *)(param_1 + 700) != 0) || (local_30 = TT_Get_MM_Var(param_1,0), local_30 == 0)) {
    puVar6 = *(uint **)(param_1 + 700);
    puVar7 = (uint *)puVar6[3];
    if (*puVar7 < param_2) {
      param_2 = *puVar7;
    }
    for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
      if (DAT_005f373c <= *(int *)(param_3 + uVar3 * 4) + 0x10000U) {
        return 6;
      }
    }
    local_28 = param_3;
    if (((*(char *)(param_1 + 0x2b8) != '\0') || (puVar6[0x12] != 0)) ||
       (local_30 = ft_var_load_gvar(param_1), local_30 == 0)) {
      if (puVar6[1] == 0) {
        uVar3 = ft_mem_realloc(local_2c,4,0,*puVar7,0,&local_30);
        puVar6[1] = uVar3;
        if (local_30 != 0) {
          return local_30;
        }
        bVar2 = true;
      }
      if (puVar6[2] == 0) {
        uVar3 = ft_mem_realloc(local_2c,4,0,*puVar7,0,&local_30);
        puVar6[2] = uVar3;
        if (local_30 != 0) {
          return local_30;
        }
        bVar8 = 1;
      }
      else {
        bVar1 = false;
        bVar8 = 0;
        for (uVar3 = 0; uVar3 < param_2; uVar3 = uVar3 + 1) {
          if (*(int *)(puVar6[2] + uVar3 * 4) != *(int *)(local_28 + uVar3 * 4)) {
            bVar8 = 2;
            bVar1 = true;
            break;
          }
        }
        if ((*(uint *)(param_1 + 4) & DAT_005f3740) == 0) {
          piVar4 = (int *)(puVar6[2] + uVar3 * 4);
          for (uVar9 = uVar3; uVar9 < *puVar7; uVar9 = uVar9 + 1) {
            if (*piVar4 != 0) {
              bVar1 = true;
            }
            piVar4 = piVar4 + 1;
          }
        }
        else {
          piVar5 = (int *)(puVar6[2] + uVar3 * 4);
          piVar4 = (int *)(puVar6[5] + *puVar7 * (*(uint *)(param_1 + 4) >> 0x10) * 4 + uVar3 * 4);
          for (uVar9 = uVar3; uVar9 < *puVar7; uVar9 = uVar9 + 1) {
            if (*piVar5 != *piVar4) {
              bVar1 = true;
            }
            piVar4 = piVar4 + 1;
            piVar5 = piVar5 + 1;
          }
        }
        if (!bVar1) {
          return -1;
        }
        for (; uVar3 < *puVar7; uVar3 = uVar3 + 1) {
          if (*(int *)(puVar6[2] + uVar3 * 4) != 0) {
            bVar8 = 2;
            break;
          }
        }
      }
      *puVar6 = *puVar7;
      FUN_00439be4(puVar6[2],local_28,param_2 << 2);
      if (param_4 != '\0') {
        if (bVar2) {
          param_2 = *puVar6;
        }
        ft_var_to_design(param_1,param_2,puVar6[2],puVar6[1]);
      }
      *(undefined1 *)(param_1 + 0x2b9) = 1;
      if ((*(int *)(param_1 + 0x29c) != 0) && (bVar8 != 0)) {
        if (bVar8 == 2) {
          ft_mem_free(local_2c,*(undefined4 *)(param_1 + 0x29c));
          *(undefined4 *)(param_1 + 0x29c) = 0;
          *(undefined4 *)(param_1 + 0x29c) = 0;
          local_30 = tt_face_load_cvt(param_1,*(undefined4 *)(param_1 + 0x68));
        }
        else if (bVar8 < 2) {
          local_30 = tt_face_vary_cvt(param_1,*(undefined4 *)(param_1 + 0x68));
        }
      }
      ft_mem_free(local_2c,*(undefined4 *)(param_1 + 0x2ac));
      *(undefined4 *)(param_1 + 0x2ac) = 0;
      *(undefined4 *)(param_1 + 0x2ac) = 0;
    }
  }
  return local_30;
}

