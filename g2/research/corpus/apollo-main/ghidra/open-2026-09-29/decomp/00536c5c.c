
void l2cSlaveRxSignalingPkt(undefined2 param_1,ushort param_2,int param_3,undefined4 param_4)

{
  char cVar1;
  char cVar2;
  byte bVar3;
  int iVar4;
  int iVar5;
  
  bVar3 = DmConnIdByHandle(param_1);
  iVar4 = DAT_00536f90;
  if (bVar3 != 0) {
    cVar1 = *(char *)(param_3 + 8);
    cVar2 = *(char *)(param_3 + 9);
    iVar5 = (uint)*(byte *)(param_3 + 0xb) * 0x100 + (uint)*(byte *)(param_3 + 10);
    if (cVar2 != '\0') {
      if (((cVar2 == *(char *)((uint)bVar3 + DAT_00536f90 + 0x13)) && ((uint)param_2 == iVar5 + 4U))
         && (((cVar1 == '\x13' && (iVar5 == 2)) || (cVar1 == '\x01')))) {
        cVar2 = *(char *)((uint)bVar3 + DAT_00536f90 + 0x10);
        *(undefined1 *)((uint)bVar3 + DAT_00536f90 + 0x13) = 0;
        iVar5 = (uint)*(byte *)(param_3 + 0xd) * 0x100 + (uint)*(byte *)(param_3 + 0xc);
        WsfTimerStop(iVar4,param_3 + 0xe);
        if (cVar2 == '\x12') {
          if (cVar1 == '\x01') {
            iVar5 = 1;
          }
          DmL2cConnUpdateCnf(param_1,iVar5);
        }
        else {
          DmL2cCmdRejInd(param_1,iVar5);
        }
      }
      else {
        iVar4 = FUN_004c9c50();
        if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00536f7c,&LAB_00536ea0,3), iVar4 != 0)) {
          iVar4 = FUN_004c9c50();
          if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00536f7c,DAT_00536f7c,4), iVar4 != 0)) {
            iVar4 = FUN_004c9c50();
            if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00536f7c,DAT_00536f8c,4), iVar4 != 0)) {
              iVar4 = FUN_004c9c50();
              if (iVar4 == 0) {
                iVar4 = FUN_004c9c50();
                if ((iVar4 == 0) ||
                   (iVar4 = FUN_0044b610(&DAT_00536f78,&LAB_00536e9c,3), iVar4 != 0)) {
                  WsfTrace(DAT_00536f7c,DAT_00536f94,cVar1,iVar5,param_2);
                }
              }
              else {
                iVar4 = FUN_0043d0ce();
                if (iVar4 << 0x1e < 0) {
                  FUN_0043d574(4,&DAT_00536f78,DAT_00536f88,DAT_00536f98,0x9e,DAT_00536f94,cVar1,
                               iVar5,param_2);
                }
              }
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                FUN_0043d574(3,&DAT_00536f78,DAT_00536f88,DAT_00536f98,0x9e,DAT_00536f94,cVar1,iVar5
                             ,param_2);
              }
            }
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              FUN_0043d574(2,&DAT_00536f78,DAT_00536f88,DAT_00536f98,0x9e,DAT_00536f94,cVar1,iVar5,
                           param_2);
            }
          }
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,&DAT_00536f78,DAT_00536f88,DAT_00536f98,0x9e,DAT_00536f94,cVar1,iVar5,
                         param_2,param_4);
          }
        }
        if (cVar1 != '\x01') {
          l2cSendCmdReject(param_1,cVar2,0);
        }
      }
    }
  }
  return;
}

