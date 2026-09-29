
undefined4 FUN_004c8210(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  
  piVar1 = *(int **)(param_1 + 0x48);
  if (piVar1 != (int *)0x0) {
    if (*piVar1 != 0) {
      FUN_004c6ee0(*piVar1);
      FUN_0044f758(*piVar1);
    }
    if (piVar1[7] != 0) {
      FUN_0048b216(piVar1[7]);
    }
    if (piVar1[8] != 0) {
      FUN_0048b216(piVar1[8]);
    }
    FUN_0044f758(piVar1[1]);
    FUN_0044f758(piVar1);
    *(undefined4 *)(param_1 + 0x48) = 0;
  }
  return param_4;
}

