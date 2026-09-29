
undefined8 FUN_0050367c(int param_1)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  if (*(char *)(param_1 + 3) == '\0') {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005040c4,&DAT_00503860,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005040c4,DAT_005040d4,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_005040c4,DAT_005040c4,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00503864,&DAT_00503868,3), iVar2 != 0)) {
              uVar1 = FUN_00503d14();
              WsfTrace(DAT_005040c4,DAT_005040c8,uVar1);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              uVar1 = FUN_00503d14();
              unaff_r5 = 0x112;
              unaff_r6 = DAT_005040c8;
              FUN_0043d574(4,&DAT_00503864,DAT_005040d0,DAT_005040cc,0x112,DAT_005040c8,uVar1);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            uVar1 = FUN_00503d14();
            unaff_r5 = 0x112;
            unaff_r6 = DAT_005040c8;
            FUN_0043d574(3,&DAT_00503864,DAT_005040d0,DAT_005040cc,0x112,DAT_005040c8,uVar1);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar1 = FUN_00503d14();
          unaff_r5 = 0x112;
          unaff_r6 = DAT_005040c8;
          FUN_0043d574(2,&DAT_00503864,DAT_005040d0,DAT_005040cc,0x112,DAT_005040c8,uVar1);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar1 = FUN_00503d14();
        unaff_r5 = 0x112;
        unaff_r6 = DAT_005040c8;
        FUN_0043d574(1,&DAT_00503864,DAT_005040d0,DAT_005040cc,0x112,DAT_005040c8,uVar1);
      }
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

