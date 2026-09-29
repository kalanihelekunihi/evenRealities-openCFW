
int cff_index_get_pointers(int *param_1,undefined4 *param_2,int *param_3,int *param_4)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  int local_30;
  int local_2c;
  undefined4 *local_28;
  
  local_30 = 0;
  uVar5 = *(undefined4 *)(*param_1 + 0x1c);
  iVar4 = 0;
  *param_2 = 0;
  local_28 = param_2;
  if (((((param_1[7] != 0) || (local_30 = cff_index_load_offsets(param_1), local_30 == 0)) &&
       (local_2c = param_1[3] + param_1[6], param_1[3] != 0)) &&
      (piVar1 = (int *)ft_mem_realloc(uVar5,4,0,param_1[3] + 1,0,&local_30), local_30 == 0)) &&
     ((param_3 == (int *)0x0 || (iVar4 = ft_mem_alloc(uVar5,local_2c,&local_30), local_30 == 0)))) {
    iVar6 = 0;
    iVar2 = param_1[8];
    if (param_3 == (int *)0x0) {
      *piVar1 = iVar2;
    }
    else {
      *piVar1 = iVar4;
    }
    uVar3 = 0;
    for (uVar7 = 1; uVar7 <= (uint)param_1[3]; uVar7 = uVar7 + 1) {
      uVar9 = *(int *)(param_1[7] + uVar7 * 4) - 1;
      uVar8 = uVar3;
      if ((uVar3 <= uVar9) && (uVar8 = uVar9, (uint)param_1[6] < uVar9)) {
        uVar8 = param_1[6];
      }
      if (param_3 == (int *)0x0) {
        piVar1[uVar7] = iVar2 + uVar8;
      }
      else {
        piVar1[uVar7] = iVar4 + uVar8 + iVar6;
        if (uVar8 != uVar3) {
          FUN_00439be4(piVar1[uVar7 - 1],uVar3 + iVar2,piVar1[uVar7] - piVar1[uVar7 - 1]);
          *(undefined1 *)piVar1[uVar7] = 0;
          piVar1[uVar7] = piVar1[uVar7] + 1;
          iVar6 = iVar6 + 1;
        }
      }
      uVar3 = uVar8;
    }
    *local_28 = piVar1;
    if (param_3 != (int *)0x0) {
      *param_3 = iVar4;
    }
    if (param_4 != (int *)0x0) {
      *param_4 = local_2c;
    }
  }
  return local_30;
}

