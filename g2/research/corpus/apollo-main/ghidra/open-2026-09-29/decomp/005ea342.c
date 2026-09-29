
undefined4 FUN_005ea342(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 in_r3;
  
  piVar1 = DAT_005eadb4;
  if ((*DAT_005eadb4 != 0) && (DAT_005eadb4[0x78] == 0)) {
    iVar2 = FUN_0043de82(*DAT_005eadb4);
    piVar1[0x78] = iVar2;
    FUN_0043f4c0(piVar1[0x78],0x240,0x120);
    FUN_0043f09a(piVar1[0x78],0,0);
    FUN_0043dfa4(piVar1[0x78],0x10);
    FUN_0044129e(piVar1[0x78],0,0);
    FUN_0044131c(piVar1[0x78],0,0);
    FUN_005ea224(piVar1[0x78],0,0);
    FUN_0044146a(piVar1[0x78],0,0);
    iVar2 = FUN_00498668(piVar1[0x78]);
    piVar1[0x79] = iVar2;
    FUN_00498680(piVar1[0x79],DAT_005eadc0);
    FUN_0043f4c0(piVar1[0x79],0x3fffffff,0x3fffffff);
    FUN_0043f09a(piVar1[0x79],0x1c,0x1c);
    iVar2 = FUN_0043de82(piVar1[0x78]);
    piVar1[0x7a] = iVar2;
    FUN_0043f4c0(piVar1[0x7a],0x240,0x3fffffff);
    FUN_0043f6b8(piVar1[0x7a],4,0,0xfffffffc);
    FUN_0043dfa4(piVar1[0x7a],0x10);
    FUN_0044129e(piVar1[0x7a],0,0);
    FUN_0044131c(piVar1[0x7a],0,0);
    FUN_005ea224(piVar1[0x7a],0,0);
    FUN_0044146a(piVar1[0x7a],0,0);
    iVar2 = FUN_00498668(piVar1[0x7a]);
    piVar1[0x7b] = iVar2;
    FUN_00498680(piVar1[0x7b],DAT_005eadc4);
    FUN_0043f4c0(piVar1[0x7b],0x3fffffff,0x3fffffff);
    uVar3 = FUN_005ea2d4();
    FUN_0043f09a(piVar1[0x7b],6,uVar3);
    iVar2 = FUN_00499416(piVar1[0x7a]);
    piVar1[0x7c] = iVar2;
    FUN_0043f09a(piVar1[0x7c],0x1c,0);
    FUN_0043f506(piVar1[0x7c],0x224);
    FUN_00499678(piVar1[0x7c],0);
    FUN_0049942e(piVar1[0x7c],DAT_005eadc8);
    uVar3 = FUN_0044104c(0xffffff);
    FUN_0044140e(piVar1[0x7c],uVar3,0);
    FUN_0044145a(piVar1[0x7c],1,0);
    FUN_0044143e(piVar1[0x7c],*DAT_005eadbc,0);
  }
  return in_r3;
}

