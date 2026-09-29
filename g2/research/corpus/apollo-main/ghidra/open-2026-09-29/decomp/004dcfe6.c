
void FUN_004dcfe6(int *param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int local_70;
  undefined4 local_6c;
  undefined4 local_60;
  int *local_54;
  undefined4 local_50;
  undefined4 local_40;
  
  if ((param_1 != (int *)0x0) && (*param_1 != 0)) {
    FUN_004503d6(&local_70);
    local_70 = *param_1;
    uVar1 = FUN_0044e498(*param_1);
    FUN_004506ce(&local_70,uVar1,param_2);
    local_6c = DAT_004dd49c;
    local_50 = DAT_004dd4a0;
    local_60 = DAT_004dd4a4;
    local_54 = param_1;
    local_40 = param_3;
    FUN_00450408(&local_70);
  }
  return;
}

