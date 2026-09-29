
undefined8 FUN_0047eab8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_18;
  
  FUN_004420d0();
  uVar2 = DAT_0047eb84;
  piVar1 = DAT_0047eb6c;
  local_18 = param_3;
  if (*DAT_0047eb6c == 0) {
    vListInitialise(DAT_0047eb84);
    uVar3 = DAT_0047eb88;
    vListInitialise(DAT_0047eb88);
    *DAT_0047eb78 = uVar2;
    *DAT_0047eb7c = uVar3;
    local_18 = 0;
    iVar4 = FUN_004415ca(0x32,0x10,DAT_0047eb90,DAT_0047eb8c);
    *piVar1 = iVar4;
  }
  FUN_004420e8();
  return CONCAT44(param_4,local_18);
}

