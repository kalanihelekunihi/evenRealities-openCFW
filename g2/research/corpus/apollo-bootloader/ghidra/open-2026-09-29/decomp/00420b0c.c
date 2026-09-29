
undefined8 FUN_00420b0c(uint param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  
  iVar1 = 0;
  if (((*DAT_00421010 == 0) || (param_2 == 0)) || (param_3 == 0)) {
    FUN_00415fae(DAT_00421058,*DAT_00421010,param_2,param_3,param_3,param_4);
    iVar1 = 6;
    uVar4 = param_3;
  }
  else if (param_1 < 0x2000000) {
    uVar4 = param_3;
    FUN_0041ff08();
    FUN_00420f10();
    uVar2 = param_1 & 0xff;
    for (; param_3 != 0; param_3 = param_3 - uVar3) {
      uVar3 = 0x100 - uVar2;
      if (param_3 <= 0x100 - uVar2) {
        uVar3 = param_3;
      }
      iVar1 = FUN_004207f4();
      if (iVar1 != 0) {
        FUN_00415fae(DAT_00421060,param_1,uVar3);
        iVar1 = 4;
        break;
      }
      iVar1 = FUN_00420984();
      if (iVar1 != 0) {
        FUN_00415fae(DAT_00421064,param_1,uVar3,iVar1);
        break;
      }
      uVar4 = uVar3;
      iVar1 = FUN_0042069e(2,param_1,1,param_2);
      if (iVar1 != 0) {
        FUN_00415fae(DAT_00421068,param_1,uVar3,iVar1);
        break;
      }
      iVar1 = FUN_004207a2(10);
      if (iVar1 != 0) {
        FUN_00415fae(DAT_0042106c,param_1,uVar3);
        iVar1 = 4;
        break;
      }
      iVar1 = FUN_004209c4();
      if (iVar1 != 0) {
        FUN_00415fae(DAT_00421070,param_1,uVar3,iVar1);
        break;
      }
      param_1 = uVar3 + param_1;
      param_2 = param_2 + uVar3;
      uVar2 = 0;
    }
    FUN_00420e8c();
    FUN_0041ff1e();
  }
  else {
    FUN_00415fae(DAT_0042105c,param_1,0x2000000,param_4,param_3,param_4);
    iVar1 = 5;
    uVar4 = param_3;
  }
  return CONCAT44(uVar4,iVar1);
}

