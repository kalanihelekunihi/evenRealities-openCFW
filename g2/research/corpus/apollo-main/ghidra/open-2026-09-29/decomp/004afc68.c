
void nvdbSysDtMarkLegacyPsn(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 in_r3;
  uint uVar3;
  undefined4 local_b0 [40];
  undefined4 uStack_10;
  
  uVar1 = DAT_004aff98;
  uStack_10 = in_r3;
  FUN_00439c04(local_b0,DAT_004b0370,0xa0);
  uVar3 = 0;
  while( true ) {
    if (0x27 < uVar3) {
      return;
    }
    iVar2 = FUN_0044b610(uVar1,local_b0[uVar3],0xf);
    if (iVar2 == 0) break;
    uVar3 = uVar3 + 1;
  }
  *DAT_004b0374 = 1;
  return;
}

