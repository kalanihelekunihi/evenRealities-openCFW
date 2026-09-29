
undefined4
SVC_IsOnWhitelistByIdentifier(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  uint uVar5;
  byte bVar6;
  
  cVar2 = service_ancc_state_byte4_get();
  if (cVar2 == '\x01') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6b60,0x13a,DAT_004d6b5c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004d6b64,DAT_004d6b64);
    }
    uVar4 = 2;
  }
  else if (param_1 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004d6af8,DAT_004d6af4,DAT_004d6b60,0x13f,DAT_004d6b68,DAT_004d6b60,0x13f,
                   param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_004d6b6c,DAT_004d6b6c,DAT_004d6b60,0x13f);
    }
    uVar4 = 0;
  }
  else {
    uVar5 = FUN_0044a43c(param_1);
    if (uVar5 < 0x40) {
      iVar3 = FUN_0044b610(DAT_004d6b78,param_1,0xb);
      if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_004d6b7c,param_1,0xb), iVar3 == 0)) {
        uVar4 = 2;
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6b60,0x17d,DAT_004d6b80,DAT_004d6b58[1]);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004d6b84,DAT_004d6b84,DAT_004d6b58[1]);
        }
        pbVar1 = DAT_004d6b58;
        if (((*DAT_004d6b58 & 0x1f) >> 4 != 0) && (DAT_004d6b58[1] != 0)) {
          for (bVar6 = 0; bVar6 < pbVar1[1]; bVar6 = bVar6 + 1) {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6b60,0x182,DAT_004d6b88,bVar6,
                           pbVar1 + (uint)bVar6 * 0x50 + 2);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x10800000,DAT_004d6b8c,DAT_004d6b8c,bVar6,
                                  pbVar1 + (uint)bVar6 * 0x50 + 2);
            }
            uVar4 = FUN_0044a43c(pbVar1 + (uint)bVar6 * 0x50 + 2);
            iVar3 = FUN_0044b610(pbVar1 + (uint)bVar6 * 0x50 + 2,param_1,uVar4);
            if (iVar3 == 0) {
              return 2;
            }
          }
        }
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004d6af8,DAT_004d6af4,DAT_004d6b60,400,DAT_004d6b90,param_1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004d6b94,DAT_004d6b94,param_1);
        }
        uVar4 = 1;
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004d6af8,DAT_004d6af4,DAT_004d6b60,0x143,DAT_004d6b70,DAT_004d6b60,0x143,
                     param_4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_004d6b74,DAT_004d6b74,DAT_004d6b60,0x143);
      }
      uVar4 = 0;
    }
  }
  return uVar4;
}

