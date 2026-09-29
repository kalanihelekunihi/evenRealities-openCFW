
void FUN_005ec770(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_005ec7dc;
  if (DAT_005ec7dc[0x8c] != 0) {
    iVar2 = FUN_0044dca2(DAT_005ec7dc[0x8c]);
    if (iVar2 == 0) {
      FUN_0044d7b8(piVar1[0x8c]);
    }
    else {
      FUN_0044d7b8();
    }
    piVar1[0x8c] = 0;
    piVar1[0x8d] = 0;
    piVar1[0x8e] = 0;
    piVar1[0x8f] = 0;
    uVar3 = td_counter_b_get();
    FUN_005e5484(4,uVar3,0);
  }
  if (*piVar1 != 0) {
    FUN_00441488(*piVar1,0xff,0);
  }
  return;
}

