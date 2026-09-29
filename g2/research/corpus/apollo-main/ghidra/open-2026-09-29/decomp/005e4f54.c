
undefined4 FUN_005e4f54(undefined4 param_1,char param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    uVar5 = 0xfffffff8;
  }
  else {
    uVar5 = 8;
  }
  uVar2 = FUN_0043de82(param_1);
  FUN_0043f4c0(uVar2,0x23c,0x3fffffff);
  if (param_2 == '\x01') {
    uVar4 = 0;
    uVar3 = 2;
  }
  else {
    uVar4 = 0xfffffff6;
    uVar3 = 5;
  }
  FUN_0043f6b8(uVar2,uVar3,0,uVar4);
  uVar4 = FUN_0044104c(0);
  FUN_0044127e(uVar2,uVar4,0);
  FUN_0044129e(uVar2,0xff,0);
  FUN_0044131c(uVar2,0,0);
  FUN_0044146a(uVar2,0,0);
  FUN_005e47cc(uVar2,0,0);
  FUN_0043dfa4(uVar2,0x10);
  uVar2 = FUN_0043de82(uVar2);
  FUN_0043f506(uVar2,0x22c);
  FUN_0043f6b8(uVar2,2,uVar5,0);
  uVar5 = FUN_0044104c(0);
  FUN_0044127e(uVar2,uVar5,0);
  FUN_0044129e(uVar2,0xff,0);
  FUN_0044131c(uVar2,1,0);
  uVar5 = FUN_0044104c(0xffffff);
  FUN_004412ec(uVar2,uVar5,0);
  FUN_0044146a(uVar2,6,0);
  FUN_005e47cc(uVar2,0,0);
  FUN_0043dfa4(uVar2,0x10);
  return uVar2;
}

