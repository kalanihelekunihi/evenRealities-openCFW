
undefined8
FUN_004212d8(undefined4 param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = param_3 + param_2 * 0x1000 + 0x1400000;
  iVar4 = param_2;
  iVar1 = FUN_00420f70(iVar3,param_4,param_5,param_4,param_2,param_3,param_4);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    FUN_00415fae(DAT_004213c8,param_2,param_3,param_5,iVar3,iVar1);
    uVar2 = 0xfffffffb;
    iVar4 = iVar3;
  }
  return CONCAT44(iVar4,uVar2);
}

