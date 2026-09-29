
void FUN_004fb568(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int local_78;
  undefined4 local_74;
  undefined4 local_68;
  undefined4 local_58;
  int local_48;
  undefined4 uStack_18;
  
  if (param_1 != 0) {
    uStack_18 = param_4;
    FUN_0043f66c(*DAT_004fb71c);
    iVar1 = FUN_0044e498(param_1);
    if (param_2 == iVar1) {
      param_3 = 10;
    }
    if (param_3 < 1) {
      FUN_0044ea04(param_1,param_2,0);
    }
    else {
      FUN_004503d6(&local_78);
      local_78 = param_1;
      FUN_004506ce(&local_78,iVar1,param_2);
      local_74 = DAT_004fb758;
      local_68 = DAT_004fb75c;
      local_58 = DAT_004fc1c0;
      *DAT_004fb738 = 1;
      local_48 = param_3;
      FUN_00450408(&local_78);
    }
  }
  return;
}

