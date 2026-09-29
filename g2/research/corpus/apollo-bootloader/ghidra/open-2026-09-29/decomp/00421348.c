
undefined8 FUN_00421348(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = param_2 * 0x1000 + 0x1400000;
  iVar1 = FUN_00420a08(iVar3);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    FUN_00415fae(DAT_004213d0,param_2,iVar3,iVar1);
    uVar2 = 0xfffffffb;
  }
  return CONCAT44(param_4,uVar2);
}

