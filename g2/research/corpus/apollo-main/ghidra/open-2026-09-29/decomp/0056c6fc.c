
void attsProcMtuReq(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  ushort uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  byte local_18 [4];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  AttsCsfGetFeatures(*(undefined1 *)(param_1 + 0x24),local_18,1);
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056cd9c,&DAT_0056c924,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056cd9c,DAT_0056cd9c,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0056cd9c,DAT_0056cdac,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0056c928,&LAB_0056c92c,3), iVar2 != 0)) {
            WsfTrace(DAT_0056cd9c,DAT_0056cda0,local_18[0]);
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_0056c928,DAT_0056cda8,DAT_0056cda4,0xff,DAT_0056cda0,local_18[0]);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_0056c928,DAT_0056cda8,DAT_0056cda4,0xff,DAT_0056cda0,local_18[0]);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_0056c928,DAT_0056cda8,DAT_0056cda4,0xff,DAT_0056cda0,local_18[0]);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_0056c928,DAT_0056cda8,DAT_0056cda4,0xff,DAT_0056cda0,local_18[0]);
    }
  }
  if ((int)((uint)local_18[0] << 0x1e) < 0) {
    attsErrRsp(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),2,0,6);
  }
  else {
    uVar3 = (uint)*(byte *)(param_3 + 10) * 0x100 + (uint)*(byte *)(param_3 + 9);
    if (uVar3 < 0xf7) {
      uVar3 = 0xf7;
    }
    uVar1 = HciGetMaxRxAclLen();
    if ((int)(uint)*(ushort *)(*DAT_0056cdb0 + 4) < (int)(uVar1 - 4)) {
      uVar4 = (uint)*(ushort *)(*DAT_0056cdb0 + 4);
    }
    else {
      iVar2 = HciGetMaxRxAclLen();
      uVar4 = iVar2 - 4;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0056cdb8,DAT_0056cda8,DAT_0056cda4,0x115,DAT_0056cdb4,uVar3,uVar4 & 0xffff)
      ;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0056cdbc,DAT_0056cdbc,uVar3,uVar4 & 0xffff);
    }
    iVar2 = attMsgAlloc(0xb);
    if (iVar2 != 0) {
      *(undefined1 *)(iVar2 + 8) = 3;
      *(char *)(iVar2 + 9) = (char)uVar4;
      *(char *)(iVar2 + 10) = (char)(uVar4 >> 8);
      attL2cDataReq(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),3);
    }
    attSetMtu(*(undefined4 *)(param_1 + 0x10),*(undefined1 *)(param_1 + 0x25),uVar3,uVar4 & 0xffff);
  }
  return;
}

