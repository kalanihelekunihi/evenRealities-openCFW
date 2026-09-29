
void af_latin_sort_blue(uint param_1,int param_2)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  
  uVar2 = 1;
  do {
    uVar1 = uVar2;
    if (param_1 <= uVar2) {
      return;
    }
    for (; uVar1 != 0; uVar1 = uVar1 - 1) {
      if ((*(byte *)(*(int *)(param_2 + uVar1 * 4 + -4) + 0x20) & 6) == 0) {
        iVar5 = *(int *)(*(int *)(param_2 + uVar1 * 4 + -4) + 0xc);
      }
      else {
        iVar5 = **(int **)(param_2 + uVar1 * 4 + -4);
      }
      if ((*(byte *)(*(int *)(param_2 + uVar1 * 4) + 0x20) & 6) == 0) {
        iVar3 = *(int *)(*(int *)(param_2 + uVar1 * 4) + 0xc);
      }
      else {
        iVar3 = **(int **)(param_2 + uVar1 * 4);
      }
      if (iVar5 <= iVar3) break;
      uVar4 = *(undefined4 *)(param_2 + uVar1 * 4);
      *(undefined4 *)(param_2 + uVar1 * 4) = *(undefined4 *)(param_2 + uVar1 * 4 + -4);
      *(undefined4 *)(param_2 + uVar1 * 4 + -4) = uVar4;
    }
    uVar2 = uVar2 + 1;
  } while( true );
}

