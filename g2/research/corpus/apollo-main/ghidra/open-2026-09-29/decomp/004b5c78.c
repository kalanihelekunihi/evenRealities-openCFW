
undefined8
dmConnCcbAlloc(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  
  bVar3 = 0;
  iVar2 = DAT_004b6520;
  do {
    if (2 < bVar3) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b6014,&DAT_004b6014,3), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b6014,DAT_004b67d0,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004b6014,DAT_004b67cc,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if (iVar2 == 0) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&LAB_004b6018,&DAT_004b5eec,3), iVar2 != 0))
              {
                WsfTrace(&DAT_004b6014,DAT_004b6884);
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                param_2 = 0xc4;
                FUN_0043d574(4,&LAB_004b6018,DAT_004b652c,DAT_004b67e4,0xc4,DAT_004b6884);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              param_2 = 0xc4;
              FUN_0043d574(3,&LAB_004b6018,DAT_004b652c,DAT_004b67e4,0xc4,DAT_004b6884);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            param_2 = 0xc4;
            FUN_0043d574(2,&LAB_004b6018,DAT_004b652c,DAT_004b67e4,0xc4,DAT_004b6884);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          param_2 = 0xc4;
          FUN_0043d574(1,&LAB_004b6018,DAT_004b652c,DAT_004b67e4,0xc4,DAT_004b6884);
        }
      }
      iVar2 = 0;
LAB_004b5ee8:
      return CONCAT44(param_2,iVar2);
    }
    if (*(char *)(iVar2 + 0x16) == '\0') {
      FUN_0043c0e4(iVar2,0x30,0,param_4,param_2,param_3,param_4);
      FUN_004d293c(iVar2,param_1);
      *(undefined2 *)(iVar2 + 0xc) = 0xffff;
      *(byte *)(iVar2 + 0x10) = bVar3 + 1;
      *(undefined1 *)(iVar2 + 0x11) = 0;
      *(undefined1 *)(iVar2 + 0x16) = 1;
      *(undefined1 *)(iVar2 + 0x2c) = 0;
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b67dc,&DAT_004b5de0,3), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b67dc,DAT_004b67d0,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004b67dc,DAT_004b67cc,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if (iVar1 == 0) {
              iVar1 = FUN_004c9c50();
              if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b5de4,&DAT_004b5eec,3), iVar1 != 0))
              {
                WsfTrace(DAT_004b67dc,DAT_004b67e0,*(undefined1 *)(iVar2 + 0x10));
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                param_2 = 0xbe;
                FUN_0043d574(4,&DAT_004b5de4,DAT_004b652c,DAT_004b67e4,0xbe,DAT_004b67e0,
                             *(undefined1 *)(iVar2 + 0x10));
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              param_2 = 0xbe;
              FUN_0043d574(3,&DAT_004b5de4,DAT_004b652c,DAT_004b67e4,0xbe,DAT_004b67e0,
                           *(undefined1 *)(iVar2 + 0x10));
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_2 = 0xbe;
            FUN_0043d574(2,&DAT_004b5de4,DAT_004b652c,DAT_004b67e4,0xbe,DAT_004b67e0,
                         *(undefined1 *)(iVar2 + 0x10));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0xbe;
          FUN_0043d574(1,&DAT_004b5de4,DAT_004b652c,DAT_004b67e4,0xbe,DAT_004b67e0,
                       *(undefined1 *)(iVar2 + 0x10));
        }
      }
      goto LAB_004b5ee8;
    }
    bVar3 = bVar3 + 1;
    iVar2 = iVar2 + 0x30;
  } while( true );
}

