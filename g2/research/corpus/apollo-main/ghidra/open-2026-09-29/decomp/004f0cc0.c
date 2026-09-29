
undefined4 FUN_004f0cc0(int param_1,undefined4 param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = FUN_0043de82();
    uVar2 = FUN_004515d2(100);
    FUN_0043f506(uVar1,uVar2);
    FUN_0043f568(uVar1,0x50);
    FUN_0043f0e0(uVar1,0);
    FUN_0043f142(uVar1,param_2);
    FUN_0044129e(uVar1,0,0);
    FUN_0044131c(uVar1,0,0);
    FUN_004effa8(uVar1,0,0);
    FUN_0044146a(uVar1,6,0);
    FUN_0043dfa4(uVar1,0x10);
    uVar2 = FUN_0043de82(uVar1);
    FUN_0043f4c0(uVar2,0x3fffffff);
    FUN_0044129e(uVar2,0,0);
    FUN_0044131c(uVar2,0,0);
    FUN_004effa8(uVar2,0,0);
    FUN_0048ba78(uVar2,0);
    FUN_0048ba92(uVar2,2,2,2);
    FUN_00441254(uVar2,8,0);
    FUN_0043f6b8(uVar2,9,0,0);
    uVar3 = FUN_00498668(uVar2);
    FUN_00498680(uVar3,DAT_004f1540);
    FUN_0043f506(uVar3,0x18);
    FUN_0043f568(uVar3,0x18);
    FUN_0043ded4(uVar3,0x10000);
    FUN_0043dfa4(uVar3,0x10);
    uVar3 = FUN_00499416(uVar2);
    uVar2 = DAT_004f1888;
    uVar4 = FUN_00460084(DAT_004f1888);
    uVar2 = FUN_0045fffe(uVar2,uVar4);
    FUN_0049942e(uVar3,uVar2);
    FUN_0044143e(uVar3,*DAT_004f0f18,0);
    uVar2 = FUN_0044104c(0xffffff);
    FUN_0044140e(uVar3,uVar2,0);
  }
  return uVar1;
}

