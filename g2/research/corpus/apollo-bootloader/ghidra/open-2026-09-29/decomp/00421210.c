
undefined4 FUN_00421210(void)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  int local_14;
  undefined4 uStack_10;
  
  uVar2 = DAT_0042139c;
  uVar1 = DAT_0042138c;
  uStack_10 = in_r3;
  iVar3 = FUN_00415132(DAT_0042138c,DAT_0042139c);
  if (iVar3 != 0) {
    FUN_00415128(uVar1,uVar2);
    iVar3 = FUN_00415132(uVar1,uVar2);
    if (iVar3 != 0) {
      elog_output(2,DAT_00421384,DAT_00421380,DAT_004213b0,0x7f,DAT_004213ac,iVar3);
      return 9;
    }
  }
  iVar3 = FUN_004210c8();
  if (iVar3 != 0) {
    elog_output(2,DAT_00421384,DAT_00421380,DAT_004213b0,0x86,DAT_004213b4);
    FUN_004211b0();
  }
  *DAT_004213b8 = 1;
  uVar2 = DAT_004213bc;
  local_14 = 0;
  FUN_00415146(uVar1,DAT_004213bc,DAT_004213c0,0x103);
  FUN_004151c0(uVar1,uVar2,&local_14,4);
  local_14 = local_14 + 1;
  FUN_00415274(uVar1,uVar2);
  FUN_004151fc(uVar1,uVar2,&local_14,4);
  FUN_00415180(uVar1,uVar2);
  elog_output(4,DAT_00421384,DAT_00421380,DAT_004213b0,0x9a,DAT_004213c4,local_14);
  return 0;
}

