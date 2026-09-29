
void Ins_GETVARIATION(int *param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = **(uint **)(*param_1 + 700);
  iVar2 = *(int *)(*(int *)(*param_1 + 700) + 8);
  if (uVar3 < (uint)((param_1[5] + 1) - param_1[4])) {
    if (iVar2 == 0) {
      for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1) {
        *(undefined4 *)(param_2 + uVar1 * 4) = 0;
      }
    }
    else {
      for (uVar1 = 0; uVar1 < uVar3; uVar1 = uVar1 + 1) {
        *(int *)(param_2 + uVar1 * 4) = *(int *)(iVar2 + uVar1 * 4) >> 2;
      }
    }
  }
  else {
    param_1[3] = 0x82;
  }
  return;
}

