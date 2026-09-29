
void af_sort_pos(uint param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  
  for (uVar2 = 1; uVar1 = uVar2, uVar2 < param_1; uVar2 = uVar2 + 1) {
    for (; (uVar1 != 0 && (*(int *)(param_2 + uVar1 * 4) < *(int *)(param_2 + uVar1 * 4 + -4)));
        uVar1 = uVar1 - 1) {
      uVar3 = *(undefined4 *)(param_2 + uVar1 * 4);
      *(undefined4 *)(param_2 + uVar1 * 4) = *(undefined4 *)(param_2 + uVar1 * 4 + -4);
      *(undefined4 *)(param_2 + uVar1 * 4 + -4) = uVar3;
    }
  }
  return;
}

