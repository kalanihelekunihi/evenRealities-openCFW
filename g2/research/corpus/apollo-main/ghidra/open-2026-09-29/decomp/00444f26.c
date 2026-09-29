
undefined8
semantic_OtaParseHexAddress
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = 0;
  uStack_c = param_4;
  iVar1 = FUN_0044b63a(param_1,&DAT_00445108);
  if ((iVar1 == 0) && (iVar1 = FUN_0044b63a(param_1,&DAT_0044510c), iVar1 == 0)) {
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_00475fc0(iVar1,DAT_004455cc,&local_10);
    uVar2 = local_10;
    if (iVar1 != 1) {
      uVar2 = 0;
    }
  }
  return CONCAT44(local_10,uVar2);
}

