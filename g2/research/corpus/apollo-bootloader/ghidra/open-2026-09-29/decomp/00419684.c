
undefined8 FUN_00419684(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_18;
  
  FUN_0041b3e4();
  uVar2 = DAT_00419720;
  piVar1 = DAT_00419708;
  local_18 = param_3;
  if (*DAT_00419708 == 0) {
    FUN_0041b53c(DAT_00419720);
    uVar3 = DAT_00419724;
    FUN_0041b53c(DAT_00419724);
    *DAT_00419714 = uVar2;
    *DAT_00419718 = uVar3;
    local_18 = 0;
    iVar4 = FUN_00419c9c(0x32,0x10,DAT_0041972c,DAT_00419728);
    *piVar1 = iVar4;
  }
  FUN_0041b3fc();
  return CONCAT44(param_4,local_18);
}

