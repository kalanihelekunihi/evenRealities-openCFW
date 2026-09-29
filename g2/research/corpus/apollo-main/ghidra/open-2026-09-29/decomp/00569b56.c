
uint hciCoreResetSequence(char *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  byte *pbVar4;
  undefined8 uVar5;
  uint local_10;
  
  iVar2 = DAT_00569d48;
  iVar1 = DAT_00569d28;
  local_10 = param_4;
  if (*param_1 == '\x0e') {
    iVar3 = (uint)(byte)param_1[4] * 0x100 + (uint)(byte)param_1[3];
    pbVar4 = (byte *)(param_1 + 6);
    if (iVar3 == 0xc01) {
      HciLeSetEventMaskCmd(DAT_00569d38);
    }
    else if (iVar3 == 0xc03) {
      *DAT_00569d30 = 0;
      HciVscUpdateNvdsParam();
    }
    else if (iVar3 == 0xc63) {
      HciReadBdAddrCmd();
    }
    else {
      if (iVar3 != 0x1001) {
        if (iVar3 == 0x1009) {
          FUN_004d293c(DAT_00569d40,pbVar4);
          HciLeReadBufSizeCmd();
          return local_10;
        }
        if (iVar3 == 0x2001) {
          HciSetEventMaskPage2Cmd(DAT_00569d3c);
          return local_10;
        }
        if (iVar3 == 0x2002) {
          *(ushort *)(DAT_00569d28 + 0x7e) = (ushort)(byte)param_1[7] * 0x100 + (ushort)*pbVar4;
          *(char *)(iVar1 + 0x83) = param_1[8];
          *(undefined1 *)(iVar1 + 0x82) = *(undefined1 *)(iVar1 + 0x83);
          HciLeReadSupStatesCmd();
          return local_10;
        }
        if (iVar3 == 0x2003) {
          uVar5 = FUN_0058f182(pbVar4);
          *(undefined8 *)(DAT_00569d28 + 0x88) = uVar5;
          hciCoreReadResolvingListSize(param_1 + 0xe);
          return local_10;
        }
        if (iVar3 == 0x200f) {
          *(byte *)(DAT_00569d28 + 0x84) = *pbVar4;
          HciLeReadLocalSupFeatCmd(param_1 + 7);
          return local_10;
        }
        if (iVar3 == 0x2018) {
          if (*DAT_00569d30 < 3) {
            *DAT_00569d30 = *DAT_00569d30 + 1;
            HciLeRandCmd();
            return local_10;
          }
          *(undefined1 *)(DAT_00569d48 + 0x21) = 0;
          local_10 = param_4 & 0xff000000;
          (**(code **)(iVar2 + 8))(&local_10);
          return local_10;
        }
        if (iVar3 == 0x201c) {
          FUN_00439be4(DAT_00569d44,pbVar4,8);
          HciLeReadWhiteListSizeCmd();
          return local_10;
        }
        if (iVar3 == 0x2024) {
          if (*(int *)(DAT_00569d28 + 0xa0) != 0) {
            (**(code **)(DAT_00569d28 + 0xa0))(pbVar4,0x2024);
            return local_10;
          }
          *(undefined2 *)(DAT_00569d28 + 0x92) = 0;
          *(undefined1 *)(iVar1 + 0x94) = 0;
          *(undefined1 *)(iVar1 + 0x95) = 0;
          HciLeRandCmd();
          return local_10;
        }
        if (iVar3 == 0x202a) {
          *(byte *)(DAT_00569d28 + 0x91) = *pbVar4;
          hciCoreReadMaxDataLen(param_1 + 7);
          return local_10;
        }
        if (iVar3 == 0x202f) {
          HciLeWriteDefDataLen
                    ((uint)(byte)param_1[7] * 0x100 + (uint)*pbVar4,
                     (uint)(byte)param_1[9] * 0x100 + (uint)(byte)param_1[8],param_1 + 10);
          return local_10;
        }
        if ((1 < iVar3 - 0x203aU) && (iVar3 != 0x204a)) {
          if (iVar3 == 0xfcc4) {
            HciSetEventMaskCmd(DAT_00569d34);
            return local_10;
          }
          if (iVar3 != 0xfff2) {
            return param_4;
          }
          HciVscSetRfPowerLevelEx(6);
          return local_10;
        }
      }
      if (*(int *)(DAT_00569d28 + 0xa0) != 0) {
        (**(code **)(DAT_00569d28 + 0xa0))(pbVar4,iVar3);
      }
    }
  }
  return local_10;
}

