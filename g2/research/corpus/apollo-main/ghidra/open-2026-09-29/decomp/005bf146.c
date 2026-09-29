
undefined8 FUN_005bf146(undefined4 param_1,undefined4 param_2,int param_3,int param_4)

{
  int iVar1;
  undefined4 local_20;
  int local_1c;
  int iStack_18;
  
  local_20 = param_2;
  local_1c = param_3;
  iStack_18 = param_4;
  FUN_0043c0e4(&local_20,8,0);
  FUN_0043c0e4(&local_20,8,0);
  if (param_3 == 0x44) {
    param_3 = 0x45;
  }
  else if (param_3 == 0x45) {
    param_3 = 0x44;
  }
  if (((param_3 != 10) && (param_3 != 0x42)) && (param_3 != 0x43)) {
    if (param_3 == 0x44) {
      iVar1 = FUN_0045a568(0);
      if (iVar1 == 1) {
        local_20 = 1;
        local_1c = FUN_005546be(*DAT_005bf8a4,-(*(undefined4 **)(param_4 + 0x10))[1],
                                **(undefined4 **)(param_4 + 0x10),0x1c);
        FUN_00464bb2(0x109,&local_20,8,0);
      }
    }
    else if (param_3 == 0x45) {
      iVar1 = FUN_0045a568(0);
      if (iVar1 == 1) {
        local_20 = 1;
        local_1c = FUN_005546be(*DAT_005bf8a4,(*(undefined4 **)(param_4 + 0x10))[1],
                                **(undefined4 **)(param_4 + 0x10),0x1c);
        FUN_00464bb2(0x109,&local_20,8,0);
      }
    }
    else if ((param_3 == 0x48) && (iVar1 = FUN_0045a568(0), iVar1 == 1)) {
      FUN_00464c36(0x109,0,0,0);
    }
  }
  return CONCAT44(local_20,1);
}

