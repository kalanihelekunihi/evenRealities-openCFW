
undefined8 FUN_00450fda(int *param_1,int *param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  int local_18;
  int local_14;
  
  local_18 = param_3;
  if ((((param_1[2] < *param_2) || (param_1[3] < param_2[1])) || (param_2[2] < *param_1)) ||
     (param_2[3] < param_1[1])) {
    uVar1 = 1;
  }
  else if (param_3 == 0) {
    uVar1 = 0;
  }
  else {
    local_14 = param_1[1];
    local_18 = *param_1;
    iVar2 = FUN_00450dd4(param_2,&local_18,param_3);
    if (iVar2 == 0) {
      local_14 = param_1[1];
      local_18 = param_1[2];
      iVar2 = FUN_00450dd4(param_2,&local_18,param_3);
      if (iVar2 == 0) {
        local_14 = param_1[3];
        local_18 = *param_1;
        iVar2 = FUN_00450dd4(param_2,&local_18,param_3);
        if (iVar2 == 0) {
          local_14 = param_1[3];
          local_18 = param_1[2];
          iVar2 = FUN_00450dd4(param_2,&local_18,param_3);
          if (iVar2 == 0) {
            uVar1 = 1;
          }
          else {
            uVar1 = 0;
          }
        }
        else {
          uVar1 = 0;
        }
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      uVar1 = 0;
    }
  }
  return CONCAT44(local_18,uVar1);
}

