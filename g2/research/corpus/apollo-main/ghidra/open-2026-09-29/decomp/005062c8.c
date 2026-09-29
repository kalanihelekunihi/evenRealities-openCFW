
undefined8 FUN_005062c8(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  uint local_18;
  undefined4 uStack_14;
  
  iVar3 = DAT_00506790;
  local_18 = param_3;
  uStack_14 = param_4;
  uVar1 = FUN_00508e5c(param_1,0x20,1,&local_18);
  local_18 = local_18 | 0x80;
  uVar2 = FUN_00508e74(param_1,0x20,1,&local_18);
  uVar1 = uVar1 | uVar2;
  FUN_00505f10(param_1,10);
  do {
    if (uVar1 != 0) goto LAB_00506332;
    uVar1 = FUN_00508e5c(param_1,0x20,1,&local_18);
    if (-1 < (char)local_18) goto LAB_00506332;
    FUN_00505f10(param_1,100);
    iVar3 = iVar3 + -100;
  } while (0 < iVar3);
  uVar1 = 0xfffffffc;
LAB_00506332:
  return CONCAT44(local_18,uVar1);
}

