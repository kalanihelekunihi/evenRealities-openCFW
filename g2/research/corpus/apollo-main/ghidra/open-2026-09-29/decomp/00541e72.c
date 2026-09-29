
undefined8
smpDbAddDevice(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  undefined4 uVar4;
  
  iVar2 = DAT_0054294c;
  uVar4 = param_2;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_005429f8,&DAT_00542180,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_005429f8,DAT_0054295c,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_005429f8,DAT_005429f8,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_005420c0,&LAB_00542284,3), iVar1 != 0)) {
            WsfTrace(DAT_005429f8,DAT_00542950);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar4 = 0x85;
            FUN_0043d574(4,&DAT_005420c0,DAT_00542958,DAT_00542954,0x85,DAT_00542950);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar4 = 0x85;
          FUN_0043d574(3,&DAT_005420c0,DAT_00542958,DAT_00542954,0x85,DAT_00542950);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar4 = 0x85;
        FUN_0043d574(2,&DAT_005420c0,DAT_00542958,DAT_00542954,0x85,DAT_00542950);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar4 = 0x85;
      FUN_0043d574(1,&DAT_005420c0,DAT_00542958,DAT_00542954,0x85,DAT_00542950,param_4);
    }
  }
  bVar3 = 1;
  do {
    if (9 < bVar3) {
      iVar2 = 0;
LAB_00541fb6:
      return CONCAT44(uVar4,iVar2);
    }
    iVar1 = smpDbRecordInUse(iVar2);
    if (iVar1 == 0) {
      FUN_0043c0e4(iVar2,0x18,0);
      *(char *)(iVar2 + 6) = (char)param_2;
      FUN_004d293c(iVar2,param_1);
      goto LAB_00541fb6;
    }
    bVar3 = bVar3 + 1;
    iVar2 = iVar2 + 0x18;
  } while( true );
}

