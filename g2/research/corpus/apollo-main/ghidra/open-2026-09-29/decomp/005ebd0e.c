
void FUN_005ebd0e(void)

{
  undefined4 *puVar1;
  int *piVar2;
  int *piVar3;
  int iVar4;
  undefined4 uVar5;
  
  piVar3 = DAT_005ec2e8;
  piVar2 = DAT_005ec2e4;
  if ((*DAT_005ec2e8 != 0) && (DAT_005ec2e4[0x7d] == 0)) {
    if (*DAT_005ec2e4 != 0) {
      FUN_00441488(*DAT_005ec2e4,0x7f,0);
    }
    iVar4 = FUN_005e4f54(*piVar3,0);
    piVar2[0x7d] = iVar4;
    FUN_0043f4c0(piVar2[0x7d],0x22c,0x3fffffff);
    FUN_0044119c(piVar2[0x7d],0x50,0);
    FUN_004411aa(piVar2[0x7d],0xd8,0);
    FUN_005ebc5c(piVar2[0x7d],0,0);
    FUN_0048ba78(piVar2[0x7d],1);
    FUN_0048ba92(piVar2[0x7d],0,0,0);
    FUN_0044120e(piVar2[0x7d],8,0);
    FUN_0044122a(piVar2[0x7d],8,0);
    FUN_00441238(piVar2[0x7d],8,0);
    FUN_00441246(piVar2[0x7d],4,0);
    FUN_0043ded4(piVar2[0x7d],0x10);
    FUN_0044e3ca(piVar2[0x7d],0xc);
    FUN_0044e368(piVar2[0x7d],0);
    uVar5 = FUN_0043de82(piVar2[0x7d]);
    FUN_0043f4c0(uVar5,0x21c,0x3fffffff);
    FUN_0043dfa4(uVar5,0x10);
    FUN_0044129e(uVar5,0,0);
    FUN_0044131c(uVar5,0,0);
    FUN_005ebc5c(uVar5,0,0);
    FUN_0048ba78(uVar5,0);
    FUN_0048ba92(uVar5,0,1,0);
    FUN_00441254(uVar5,4,0);
    iVar4 = FUN_00597e90(uVar5);
    piVar2[0x7e] = iVar4;
    FUN_0043f4c0(piVar2[0x7e],0x10,0x10);
    FUN_004411e4(piVar2[0x7e],0xfffffffe,0);
    FUN_005e482a(piVar2[0x7e],DAT_005ec2ec,0x13,0x3c);
    iVar4 = FUN_00499416(uVar5);
    piVar2[0x7f] = iVar4;
    FUN_0043f4c0(piVar2[0x7f],0x208,0x3fffffff);
    FUN_00499678(piVar2[0x7f],0);
    FUN_0049942e(piVar2[0x7f],DAT_005ec2f0);
    uVar5 = FUN_0044104c(0xffffff);
    FUN_0044140e(piVar2[0x7f],uVar5,0);
    puVar1 = DAT_005ec2e0;
    FUN_0044143e(piVar2[0x7f],*DAT_005ec2e0,0);
    iVar4 = FUN_0043de82(piVar2[0x7d]);
    piVar2[0x80] = iVar4;
    FUN_0043f4c0(piVar2[0x80],0x208,0x28);
    FUN_0043dfa4(piVar2[0x80],0x10);
    FUN_0044129e(piVar2[0x80],0,0);
    FUN_0044131c(piVar2[0x80],1,0);
    uVar5 = FUN_0044104c(0xffffff);
    FUN_004412ec(piVar2[0x80],uVar5,0);
    FUN_0044132a(piVar2[0x80],2,0);
    FUN_0044146a(piVar2[0x80],0,0);
    FUN_005ebc5c(piVar2[0x80],0,0);
    FUN_00441270(piVar2[0x80],0x14,0);
    iVar4 = FUN_00499416(piVar2[0x80]);
    piVar2[0x81] = iVar4;
    FUN_0043f6b8(piVar2[0x81],7,0,0);
    FUN_0049942e(piVar2[0x81],DAT_005ec2f4);
    uVar5 = FUN_0044104c(DAT_005ec2f8);
    FUN_0044140e(piVar2[0x81],uVar5,0);
    FUN_0044143e(piVar2[0x81],*puVar1,0);
    piVar2[0x82] = 0;
    piVar2[0x83] = 0;
    piVar2[0x84] = 0;
    *(undefined1 *)(piVar2 + 0x9e) = 0;
    uVar5 = td_counter_b_get();
    FUN_005e5484(4,uVar5,2);
  }
  return;
}

