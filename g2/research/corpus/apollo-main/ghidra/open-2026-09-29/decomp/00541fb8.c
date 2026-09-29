
int smpDbGetRecord(undefined1 param_1)

{
  undefined1 uVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  byte bVar8;
  
  iVar6 = DAT_005429f4;
  uVar1 = DmConnPeerAddrType(param_1);
  cVar2 = DmHostAddrType(uVar1);
  uVar3 = DmConnPeerAddr(param_1);
  iVar4 = FUN_004c9c50();
  if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_005429f8,&DAT_00542180,3), iVar4 != 0)) {
    iVar4 = FUN_004c9c50();
    if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_005429f8,DAT_0054295c,4), iVar4 != 0)) {
      iVar4 = FUN_004c9c50();
      if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_005429f8,DAT_005429f8,4), iVar4 != 0)) {
        iVar4 = FUN_004c9c50();
        if (iVar4 == 0) {
          iVar4 = FUN_004c9c50();
          if ((iVar4 == 0) || (iVar4 = FUN_0044b610(&LAB_005422c0,&LAB_00542284,3), iVar4 != 0)) {
            WsfTrace(DAT_005429f8,DAT_00542a08,param_1,cVar2);
          }
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(4,&LAB_005422c0,DAT_00542958,DAT_00542a0c,0xa7,DAT_00542a08,param_1,cVar2);
          }
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_005420c0,DAT_00542958,DAT_00542a0c,0xa7,DAT_00542a08,param_1,cVar2);
        }
      }
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_005420c0,DAT_00542958,DAT_00542a0c,0xa7,DAT_00542a08,param_1,cVar2);
      }
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_005420c0,DAT_00542958,DAT_00542a0c,0xa7,DAT_00542a08,param_1,cVar2);
    }
  }
  bVar8 = 1;
  iVar4 = iVar6;
  while( true ) {
    iVar7 = iVar4 + 0x18;
    if (9 < bVar8) {
      iVar4 = smpDbAddDevice(uVar3,cVar2);
      if (iVar4 == 0) {
        iVar7 = FUN_004c9c50();
        iVar4 = iVar6;
        if ((iVar7 == 0) || (iVar6 = FUN_0044b610(DAT_005429f8,&DAT_00542180,3), iVar6 != 0)) {
          iVar6 = FUN_004c9c50();
          if ((iVar6 == 0) || (iVar6 = FUN_0044b610(DAT_005429f8,DAT_0054295c,4), iVar6 != 0)) {
            iVar6 = FUN_004c9c50();
            if ((iVar6 == 0) || (iVar6 = FUN_0044b610(DAT_005429f8,DAT_005429f8,4), iVar6 != 0)) {
              iVar6 = FUN_004c9c50();
              if (iVar6 == 0) {
                iVar6 = FUN_004c9c50();
                if ((iVar6 == 0) ||
                   (iVar6 = FUN_0044b610(&LAB_005422c0,&LAB_00542284,3), iVar6 != 0)) {
                  WsfTrace(DAT_005429f8,DAT_00542a10);
                }
              }
              else {
                iVar6 = FUN_0043d0ce();
                if (iVar6 << 0x1e < 0) {
                  FUN_0043d574(4,&LAB_005422c0,DAT_00542958,DAT_00542a0c,0xb6,DAT_00542a10);
                }
              }
            }
            else {
              iVar6 = FUN_0043d0ce();
              if (iVar6 << 0x1e < 0) {
                FUN_0043d574(3,&LAB_005422c0,DAT_00542958,DAT_00542a0c,0xb6,DAT_00542a10);
              }
            }
          }
          else {
            iVar6 = FUN_0043d0ce();
            if (iVar6 << 0x1e < 0) {
              FUN_0043d574(2,&LAB_005422c0,DAT_00542958,DAT_00542a0c,0xb6,DAT_00542a10);
            }
          }
        }
        else {
          iVar6 = FUN_0043d0ce();
          if (iVar6 << 0x1e < 0) {
            FUN_0043d574(1,&LAB_005422c0,DAT_00542958,DAT_00542a0c,0xb6,DAT_00542a10);
          }
        }
      }
      return iVar4;
    }
    iVar5 = smpDbRecordInUse(iVar7);
    if (((iVar5 != 0) && (*(char *)(iVar4 + 0x1e) == cVar2)) &&
       (iVar4 = FUN_004d294a(iVar7,uVar3), iVar4 != 0)) break;
    bVar8 = bVar8 + 1;
    iVar4 = iVar7;
  }
  return iVar7;
}

