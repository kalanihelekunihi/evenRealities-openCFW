
void FUN_004f76b6(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 uVar2;
  int local_78;
  undefined4 local_74;
  undefined4 local_48;
  undefined4 uStack_18;
  
  piVar1 = DAT_004f8090;
  if (*DAT_004f8090 != 0) {
    uStack_18 = param_4;
    uVar2 = FUN_004f5050(*DAT_004f8090,0x10000);
    FUN_004503d6(&local_78);
    local_78 = *piVar1;
    FUN_004506ce(&local_78,uVar2,param_1);
    local_74 = DAT_004f8324;
    local_48 = param_2;
    FUN_00450408(&local_78);
  }
  return;
}

