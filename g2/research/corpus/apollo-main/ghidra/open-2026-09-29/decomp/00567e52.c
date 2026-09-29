
undefined8 FUN_00567e52(undefined4 *param_1,int *param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int local_18;
  
  local_18 = param_4;
  if (((param_2 == (int *)0x0) || (param_1 == (undefined4 *)0x0)) || (param_1[1] == 0)) {
    iVar2 = 6;
  }
  else {
    *param_2 = 0;
    if ((param_1 == (undefined4 *)0x0) || (param_1[1] == 0)) {
      iVar2 = 6;
    }
    else {
      iVar3 = param_1[1];
      iVar2 = FUN_00567e24(*param_1,iVar3,&local_18);
      if (iVar2 == 0) {
        uVar1 = param_1[4];
        *(undefined4 *)(local_18 + 0xc) = param_1[3];
        *(undefined4 *)(local_18 + 0x10) = uVar1;
        *(undefined4 *)(local_18 + 8) = param_1[2];
        if (*(int *)(iVar3 + 0x10) != 0) {
          iVar2 = (**(code **)(iVar3 + 0x10))(param_1,local_18);
        }
        if (iVar2 == 0) {
          *param_2 = local_18;
        }
        else {
          FUN_00567f88(local_18);
        }
      }
    }
  }
  return CONCAT44(local_18,iVar2);
}

