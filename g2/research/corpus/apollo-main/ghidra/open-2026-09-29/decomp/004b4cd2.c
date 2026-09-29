
undefined8
HciVscSetCustom_BDAddr(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  
  uStack_18 = param_2;
  uStack_14 = param_3;
  uStack_10 = param_4;
  FUN_0043c0e4(&uStack_18,6,0);
  if ((param_1 == 0) || (iVar1 = FUN_004751c8(&uStack_18,param_1,6), iVar1 == 0)) {
    uVar2 = 0;
  }
  else {
    FUN_00439be4(DAT_004b4d98,param_1,6);
    uVar2 = 1;
  }
  return CONCAT44(uStack_18,uVar2);
}

