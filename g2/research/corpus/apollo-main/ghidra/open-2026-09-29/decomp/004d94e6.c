
undefined4 FUN_004d94e6(int param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  int *piVar2;
  
  if ((*(short *)(param_3 + 0x12) == 8) &&
     (piVar2 = *(int **)(param_3 + 0x1c), piVar2 != (int *)0x0)) {
    if ((param_1 != 0) && (*piVar2 != 0)) {
      uVar1 = (*(code *)*piVar2)(param_1,param_3,piVar2 + 1);
      return uVar1;
    }
    if ((param_2 != 0) && (*piVar2 != 0)) {
      uVar1 = (*(code *)*piVar2)(param_2,param_3,piVar2 + 1);
      return uVar1;
    }
  }
  return 1;
}

