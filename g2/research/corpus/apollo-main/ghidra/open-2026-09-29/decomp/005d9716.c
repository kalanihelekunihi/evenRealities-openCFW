
int FUN_005d9716(undefined4 param_1,int param_2,uint param_3,code *param_4,code *param_5,
                undefined4 param_6)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint *puVar4;
  uint uVar5;
  int local_78;
  int local_74 [10];
  uint local_4c [10];
  
  FUN_0043c0e4(local_74,0x28,0);
  *(undefined4 *)(param_2 + 0x10) = 0;
  *(undefined4 *)(param_2 + 0x14) = 0;
  uVar1 = ft_mem_realloc(param_1,8,0,param_3 + 10,0,&local_78);
  *(undefined4 *)(param_2 + 0x14) = uVar1;
  if (local_78 == 0) {
    puVar4 = *(uint **)(param_2 + 0x14);
    for (uVar5 = 0; uVar5 < param_3; uVar5 = uVar5 + 1) {
      iVar2 = (*param_4)(param_6,uVar5);
      if (iVar2 != 0) {
        FUN_005d96b6(iVar2,uVar5,local_4c,local_74);
        uVar3 = FUN_005d9580(iVar2);
        if ((uVar3 & 0x7fffffff) != 0) {
          FUN_005d96f8(uVar3,local_74);
          *puVar4 = uVar3;
          puVar4[1] = uVar5;
          puVar4 = puVar4 + 2;
        }
        if (param_5 != (code *)0x0) {
          (*param_5)(param_6,iVar2);
        }
      }
    }
    for (uVar5 = 0; uVar5 < 10; uVar5 = uVar5 + 1) {
      if (local_74[uVar5] == 1) {
        *puVar4 = *(uint *)(DAT_005d9938 + uVar5 * 4);
        puVar4[1] = local_4c[uVar5];
        puVar4 = puVar4 + 2;
      }
    }
    uVar5 = (int)puVar4 - *(int *)(param_2 + 0x14) >> 3;
    if (uVar5 == 0) {
      ft_mem_free(param_1,*(undefined4 *)(param_2 + 0x14));
      *(undefined4 *)(param_2 + 0x14) = 0;
      if (local_78 == 0) {
        local_78 = 0xa3;
      }
    }
    else {
      if (uVar5 < param_3 >> 1) {
        uVar1 = ft_mem_realloc(param_1,8,param_3,uVar5,*(undefined4 *)(param_2 + 0x14),&local_78);
        *(undefined4 *)(param_2 + 0x14) = uVar1;
        local_78 = 0;
      }
      FUN_00567c4c(*(undefined4 *)(param_2 + 0x14),uVar5,8,PTR_LAB_005d9672_1_005d993c);
    }
    *(uint *)(param_2 + 0x10) = uVar5;
  }
  return local_78;
}

