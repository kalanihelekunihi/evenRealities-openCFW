
void FUN_005ea564(int param_1,int param_2,undefined2 param_3)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  undefined1 uVar6;
  
  if ((param_1 != 0) && (param_2 != 0)) {
    iVar2 = FUN_0044dce2(param_1,0);
    if (iVar2 == 0) {
      iVar2 = FUN_00499416(param_1);
      FUN_0043f09a(iVar2,0x1c,0);
      FUN_0043f506(iVar2,0x21a);
      FUN_00499678(iVar2,0);
      FUN_0044145a(iVar2,1,0);
      FUN_0044143e(iVar2,*DAT_005eadbc,0);
      uVar3 = FUN_005ea2c2();
      FUN_0044144c(iVar2,uVar3,0);
    }
    cVar1 = FUN_005ea2f2(param_2);
    FUN_0049942e(iVar2,param_2 + 2);
    uVar3 = DAT_005eb284;
    if (cVar1 == '\0') {
      uVar3 = 0xffffff;
    }
    uVar3 = FUN_0044104c(uVar3);
    FUN_0044140e(iVar2,uVar3,0);
    FUN_0044142e(iVar2,0xff,0);
    uVar4 = FUN_0044ddea(param_1);
    if (uVar4 < 2) {
      iVar2 = 0;
    }
    else {
      iVar2 = FUN_0044dce2(param_1,1);
    }
    iVar5 = FUN_005ea524(param_3,param_2);
    if (iVar5 == 0) {
      if (iVar2 != 0) {
        FUN_0044d7b8(iVar2);
      }
    }
    else {
      if (iVar2 == 0) {
        iVar2 = FUN_00498668(param_1);
      }
      FUN_00498680(iVar2,iVar5);
      uVar3 = FUN_005ea2b0();
      FUN_0043f09a(iVar2,8,uVar3);
      if (cVar1 == '\0') {
        uVar6 = 0xff;
      }
      else {
        uVar6 = 0x33;
      }
      FUN_00441488(iVar2,uVar6,0);
    }
  }
  return;
}

