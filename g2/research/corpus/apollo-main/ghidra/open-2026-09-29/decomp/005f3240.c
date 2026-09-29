
undefined8 TT_Get_Var_Design(int param_1,uint param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint *puVar4;
  
  if (((*(int *)(param_1 + 700) != 0) || (iVar1 = TT_Get_MM_Var(param_1,0), iVar1 == 0)) &&
     ((puVar4 = *(uint **)(param_1 + 700), puVar4[1] != 0 ||
      (iVar1 = tt_set_mm_blend(param_1,0,0,1), iVar1 == 0)))) {
    uVar3 = param_2;
    if (*puVar4 < param_2) {
      uVar3 = *puVar4;
    }
    if (*(char *)(param_1 + 0x2b9) == '\0') {
      for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1) {
        *(undefined4 *)(param_3 + uVar2 * 4) = 0;
      }
    }
    else {
      for (uVar2 = 0; uVar2 < uVar3; uVar2 = uVar2 + 1) {
        *(undefined4 *)(param_3 + uVar2 * 4) = *(undefined4 *)(puVar4[1] + uVar2 * 4);
      }
    }
    for (; uVar2 < param_2; uVar2 = uVar2 + 1) {
      *(undefined4 *)(param_3 + uVar2 * 4) = 0;
    }
    iVar1 = 0;
  }
  return CONCAT44(param_4,iVar1);
}

