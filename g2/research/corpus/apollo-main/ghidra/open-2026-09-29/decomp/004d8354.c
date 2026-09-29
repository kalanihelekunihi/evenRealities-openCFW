
undefined8 get_object_item(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    piVar1 = (undefined4 *)0x0;
  }
  else {
    piVar1 = *(int **)(param_1 + 8);
    if (param_3 == 0) {
      while ((piVar1 != (undefined4 *)0x0 &&
             (iVar2 = case_insensitive_strcmp(param_2,piVar1[8]), iVar2 != 0))) {
        piVar1 = (int *)*piVar1;
      }
    }
    else {
      while (((piVar1 != (int *)0x0 && (piVar1[8] != 0)) &&
             (iVar2 = FUN_0046cacc(param_2,piVar1[8]), iVar2 != 0))) {
        piVar1 = (int *)*piVar1;
      }
    }
    if ((piVar1 == (undefined4 *)0x0) || (piVar1[8] == 0)) {
      piVar1 = (undefined4 *)0x0;
    }
  }
  return CONCAT44(param_4,piVar1);
}

