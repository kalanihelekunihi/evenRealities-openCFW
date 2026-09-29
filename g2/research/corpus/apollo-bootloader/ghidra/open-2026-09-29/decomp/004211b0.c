
undefined8 FUN_004211b0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = DAT_0042138c;
  FUN_0041513c(DAT_0042138c);
  uVar1 = DAT_0042139c;
  FUN_00415128(uVar3,DAT_0042139c);
  iVar2 = FUN_00415132(uVar3,uVar1);
  if (iVar2 == 0) {
    iVar2 = FUN_004210c8();
    if (iVar2 == 0) {
      uVar3 = 0;
    }
    else {
      param_2 = 0x6f;
      elog_output(2,DAT_00421384,DAT_00421380,DAT_004213a4,0x6f,DAT_004213a8,param_4);
      uVar3 = 9;
    }
  }
  else {
    param_2 = 0x6b;
    elog_output(2,DAT_00421384,DAT_00421380,DAT_004213a4,0x6b,DAT_004213a0,iVar2);
    uVar3 = 9;
  }
  return CONCAT44(param_2,uVar3);
}

