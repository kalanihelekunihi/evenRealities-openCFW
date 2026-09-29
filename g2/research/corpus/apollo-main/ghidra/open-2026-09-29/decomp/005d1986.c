
void FUN_005d1986(int param_1)

{
  short *psVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  
  psVar1 = *(short **)(param_1 + 0x14);
  if (psVar1 != (short *)0x0) {
    if (*psVar1 < 2) {
      iVar3 = 0;
    }
    else {
      iVar3 = *(short *)(*(int *)(psVar1 + 6) + *psVar1 * 2 + -4) + 1;
    }
    if ((*psVar1 == 0) || (iVar3 != psVar1[1])) {
      if (1 < psVar1[1]) {
        piVar2 = (int *)(*(int *)(psVar1 + 2) + iVar3 * 8);
        iVar4 = *(int *)(psVar1 + 2) + psVar1[1] * 8;
        if (((*piVar2 == *(int *)(iVar4 + -8)) && (piVar2[1] == *(int *)(iVar4 + -4))) &&
           (*(char *)(*(int *)(psVar1 + 4) + (int)psVar1[1] + -1) == '\x01')) {
          psVar1[1] = psVar1[1] + -1;
        }
      }
      if (0 < *psVar1) {
        if (iVar3 == psVar1[1] + -1) {
          *psVar1 = *psVar1 + -1;
          psVar1[1] = psVar1[1] + -1;
        }
        else {
          *(short *)(*(int *)(psVar1 + 6) + *psVar1 * 2 + -2) = psVar1[1] + -1;
        }
      }
    }
    else {
      *psVar1 = *psVar1 + -1;
    }
  }
  return;
}

