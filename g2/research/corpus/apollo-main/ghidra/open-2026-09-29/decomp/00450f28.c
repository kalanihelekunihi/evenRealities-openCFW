
undefined8 FUN_00450f28(int *param_1,int *param_2,int param_3)

{
  bool bVar1;
  undefined4 uVar2;
  int iVar3;
  int local_18;
  int local_14;
  
  bVar1 = false;
  if ((((*param_2 <= *param_1) && (param_2[1] <= param_1[1])) && (param_1[2] <= param_2[2])) &&
     (param_1[3] <= param_2[3])) {
    bVar1 = true;
  }
  local_18 = param_3;
  if (bVar1) {
    if (param_3 == 0) {
      uVar2 = 1;
    }
    else {
      local_14 = param_1[1];
      local_18 = *param_1;
      iVar3 = FUN_00450dd4(param_2,&local_18,param_3);
      if (iVar3 == 0) {
        uVar2 = 0;
      }
      else {
        local_14 = param_1[1];
        local_18 = param_1[2];
        iVar3 = FUN_00450dd4(param_2,&local_18,param_3);
        if (iVar3 == 0) {
          uVar2 = 0;
        }
        else {
          local_14 = param_1[3];
          local_18 = *param_1;
          iVar3 = FUN_00450dd4(param_2,&local_18,param_3);
          if (iVar3 == 0) {
            uVar2 = 0;
          }
          else {
            local_14 = param_1[3];
            local_18 = param_1[2];
            iVar3 = FUN_00450dd4(param_2,&local_18,param_3);
            if (iVar3 == 0) {
              uVar2 = 0;
            }
            else {
              uVar2 = 1;
            }
          }
        }
      }
    }
  }
  else {
    uVar2 = 0;
  }
  return CONCAT44(local_18,uVar2);
}

