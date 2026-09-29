
void FUN_005ec268(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_005ec2e4;
  if (DAT_005ec2e4[0x7d] != 0) {
    iVar2 = FUN_0044dca2(DAT_005ec2e4[0x7d]);
    if (iVar2 == 0) {
      FUN_0044d7b8(piVar1[0x7d]);
    }
    else {
      FUN_0044d7b8();
    }
    piVar1[0x7d] = 0;
    piVar1[0x7e] = 0;
    piVar1[0x7f] = 0;
    piVar1[0x80] = 0;
    piVar1[0x81] = 0;
    piVar1[0x82] = 0;
    piVar1[0x83] = 0;
    piVar1[0x84] = 0;
    uVar3 = td_counter_b_get();
    FUN_005e5484(4,uVar3,0);
  }
  if (*piVar1 != 0) {
    FUN_00441488(*piVar1,0xff,0);
  }
  return;
}

