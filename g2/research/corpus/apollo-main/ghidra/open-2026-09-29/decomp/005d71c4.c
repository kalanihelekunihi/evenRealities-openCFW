
int * FUN_005d71c4(uint *param_1,uint *param_2,int *param_3,undefined4 param_4,undefined4 param_5)

{
  bool bVar1;
  uint uVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int *local_20;
  undefined4 uStack_1c;
  
  uVar5 = *param_2;
  local_20 = param_3;
  uStack_1c = param_4;
  uVar2 = ft_mem_realloc(param_5,4,0,uVar5 << 1,0,&local_20);
  param_1[3] = uVar2;
  if (local_20 == (int *)0x0) {
    uVar2 = ft_mem_realloc(param_5,0x1c,0,uVar5,0,&local_20);
    param_1[2] = uVar2;
    if (local_20 == (int *)0x0) {
      uVar2 = ft_mem_realloc(param_5,0x10,0,uVar5 * 2 + 1,0,&local_20);
      param_1[6] = uVar2;
      if (local_20 == (int *)0x0) {
        bVar1 = false;
        goto LAB_005d7230;
      }
    }
  }
  bVar1 = true;
LAB_005d7230:
  if (!bVar1) {
    *param_1 = uVar5;
    param_1[4] = param_1[3] + uVar5 * 4;
    param_1[1] = 0;
    param_1[5] = 0;
    param_1[7] = 0;
    puVar3 = (undefined4 *)param_1[2];
    puVar4 = (undefined4 *)param_2[2];
    for (; uVar5 != 0; uVar5 = uVar5 - 1) {
      *puVar3 = *puVar4;
      puVar3[1] = puVar4[1];
      puVar3[4] = puVar4[2];
      puVar3 = puVar3 + 7;
      puVar4 = puVar4 + 3;
    }
    if (param_3 != (int *)0x0) {
      iVar7 = param_3[2];
      iVar6 = *param_3;
      param_1[8] = (uint)param_3;
      for (; iVar6 != 0; iVar6 = iVar6 + -1) {
        FUN_005d718a(param_1,iVar7);
        iVar7 = iVar7 + 0x10;
      }
    }
    if (param_1[1] != *param_1) {
      uVar2 = *param_1;
      for (uVar5 = 0; uVar5 < uVar2; uVar5 = uVar5 + 1) {
        FUN_005d7124(param_1,uVar5);
      }
    }
  }
  return local_20;
}

