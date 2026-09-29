
undefined8 FT_Get_Next_Char(int param_1,int param_2,undefined1 *param_3,int param_4)

{
  undefined4 uVar1;
  int *piVar2;
  int *piVar3;
  
  if (param_1 == 0) {
    uVar1 = 0x23;
  }
  else if ((param_3 == (undefined1 *)0x0) || (param_4 == 0)) {
    uVar1 = 6;
  }
  else {
    *param_3 = 0;
    if (param_2 < *(int *)(param_1 + 0x10)) {
      if (*(int *)(param_1 + 8) << 0x16 < 0) {
        piVar3 = *(int **)(*(int *)(param_1 + 0x80) + 0x28);
        if (piVar3 == (int *)0xfffffffe) {
          piVar3 = (int *)0x0;
        }
        else if (piVar3 == (int *)0x0) {
          piVar2 = *(int **)(param_1 + 0x60);
          piVar3 = (int *)0x0;
          if (*(int *)(*piVar2 + 0x20) != 0) {
            piVar3 = (int *)(**(code **)(*piVar2 + 0x20))(piVar2,DAT_005274f8);
          }
          piVar2 = (int *)0xfffffffe;
          if (piVar3 != (int *)0x0) {
            piVar2 = piVar3;
          }
          *(int **)(*(int *)(param_1 + 0x80) + 0x28) = piVar2;
        }
        if ((piVar3 == (int *)0x0) || (*piVar3 == 0)) {
          uVar1 = 6;
        }
        else {
          uVar1 = (*(code *)*piVar3)(param_1,param_2,param_3,param_4);
        }
      }
      else {
        uVar1 = 6;
      }
    }
    else {
      uVar1 = 0x10;
    }
  }
  return CONCAT44(param_4,uVar1);
}

