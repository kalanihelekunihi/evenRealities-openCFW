
void FUN_005ebbc6(void)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_005ebc34;
  if (DAT_005ebc34[0x85] != 0) {
    iVar2 = FUN_0044dca2(DAT_005ebc34[0x85]);
    if (iVar2 == 0) {
      FUN_0044d7b8(piVar1[0x85]);
    }
    else {
      FUN_0044d7b8();
    }
    piVar1[0x85] = 0;
    piVar1[0x86] = 0;
    piVar1[0x87] = 0;
    piVar1[0x88] = 0;
    *(undefined1 *)(piVar1 + 0x9f) = 0;
    uVar3 = td_counter_b_get();
    FUN_005e5484(4,uVar3,0);
  }
  if (*piVar1 != 0) {
    FUN_00441488(*piVar1,0xff,0);
  }
  return;
}

