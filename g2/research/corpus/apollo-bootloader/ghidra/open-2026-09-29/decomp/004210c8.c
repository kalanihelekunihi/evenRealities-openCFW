
undefined4 FUN_004210c8(void)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined4 local_58 [4];
  undefined1 auStack_48 [52];
  
  FUN_004156ac(local_58,DAT_00421374,0x10);
  iVar3 = 0;
  do {
    uVar1 = DAT_0042138c;
    if (3 < iVar3) {
      return 0;
    }
    iVar2 = FUN_00415288(DAT_0042138c,auStack_48,local_58[iVar3]);
    if (iVar2 == -2) {
      iVar2 = FUN_0041527e(uVar1,local_58[iVar3]);
      if (iVar2 == 0) {
        elog_output(4,DAT_00421384,DAT_00421380,DAT_0042137c,0x51,DAT_00421378,local_58[iVar3]);
      }
      else if (iVar2 == -0x11) {
        elog_output(4,DAT_00421384,DAT_00421380,DAT_0042137c,0x53,DAT_00421390,local_58[iVar3]);
      }
      else {
        elog_output(2,DAT_00421384,DAT_00421380,DAT_0042137c,0x55,DAT_00421394,local_58[iVar3],iVar2
                   );
      }
    }
    else {
      if (iVar2 != 0) {
        elog_output(2,DAT_00421384,DAT_00421380,DAT_0042137c,0x5c,DAT_00421398,local_58[iVar3],iVar2
                   );
        return 0xffffffff;
      }
      FUN_0041531c(uVar1,auStack_48);
      elog_output(4,DAT_00421384,DAT_00421380,DAT_0042137c,0x5a,DAT_00421388,local_58[iVar3]);
    }
    iVar3 = iVar3 + 1;
  } while( true );
}

