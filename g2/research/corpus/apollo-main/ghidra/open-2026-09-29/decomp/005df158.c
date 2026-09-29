
int * FUN_005df158(int param_1,int param_2)

{
  int *piVar1;
  int *piVar2;
  
  piVar1 = *(int **)(param_1 + 0x9c);
  piVar2 = piVar1 + (uint)*(ushort *)(param_1 + 0x98) * 4;
  while( true ) {
    if (piVar2 <= piVar1) {
      return (int *)0x0;
    }
    if ((*piVar1 == param_2) && (piVar1[3] != 0)) break;
    piVar1 = piVar1 + 4;
  }
  return piVar1;
}

