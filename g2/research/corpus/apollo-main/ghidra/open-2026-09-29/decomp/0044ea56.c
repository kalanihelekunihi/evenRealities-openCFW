
undefined8 FUN_0044ea56(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  uStack_20 = param_2;
  uStack_1c = param_3;
  uStack_18 = param_4;
  FUN_0043f66c(param_1);
  FUN_0043bb00(&uStack_20,0,8);
  iVar1 = FUN_0044dca2(param_1);
  iVar3 = param_1;
  while (iVar2 = iVar1, iVar2 != 0) {
    FUN_0044f40c(param_1 + 0x14,iVar3,&uStack_20,param_2 & 0xff);
    iVar1 = FUN_0044dca2(iVar2);
    iVar3 = iVar2;
  }
  return CONCAT44(uStack_1c,uStack_20);
}

