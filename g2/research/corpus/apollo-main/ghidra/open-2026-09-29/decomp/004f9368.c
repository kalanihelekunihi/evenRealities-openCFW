
undefined4 FUN_004f9368(void)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  
  puVar1 = DAT_004f9f10;
  if (*DAT_004f9f0c != 0) {
    uVar3 = FUN_0043de82(*DAT_004f9f0c);
    *puVar1 = uVar3;
    FUN_0043f4c0(*puVar1,0x222,0x3fffffff);
    FUN_0043f09a(*puVar1,0,0);
    uVar3 = FUN_0044104c(0);
    FUN_0044127e(*puVar1,uVar3,0);
    FUN_0044129e(*puVar1,0,0);
    FUN_0044146a(*puVar1,6,0);
    FUN_004f5068(*puVar1,8,0);
    FUN_0044e368(*puVar1,0);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_004412ec(*puVar1,uVar3,0);
    FUN_0044131c(*puVar1,0,0);
    FUN_0043dfa4(*puVar1,0x10);
    FUN_0043ded4(*puVar1,1);
    FUN_004f81f0();
    puVar2 = DAT_004fa044;
    uVar3 = FUN_00499416(*puVar1);
    *puVar2 = uVar3;
    FUN_0043f506(*puVar2,0x240);
    FUN_0043f568(*puVar2,0x3fffffff);
    uVar3 = DAT_004fa048;
    uVar4 = FUN_00460084(DAT_004fa048);
    uVar3 = FUN_0045fffe(uVar3,uVar4);
    FUN_0049942e(*puVar2,uVar3);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(*puVar2,uVar3,0);
    FUN_0044143e(*puVar2,*DAT_004f9478,0);
    FUN_0043f0e0(*puVar2,0x20);
    FUN_0043f142(*puVar2,0);
  }
  return in_r3;
}

