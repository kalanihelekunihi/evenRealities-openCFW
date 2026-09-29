
undefined8
attsCsfSetHashUpdateStatus(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar2 = DAT_0052d07c;
  local_10 = param_3;
  local_c = param_4;
  if (*(char *)(DAT_0052d07c + 0xc) != param_1) {
    *(char *)(DAT_0052d07c + 0xc) = param_1;
    if (param_1 == '\0') {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d35c,&DAT_0052c91c,3), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d35c,DAT_0052d08c,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(DAT_0052d35c,DAT_0052d35c,4), iVar2 != 0)) {
            iVar2 = FUN_004c9c50();
            if (iVar2 == 0) {
              iVar2 = FUN_004c9c50();
              if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_0052c920,&DAT_0052c924,3), iVar2 != 0))
              {
                WsfTrace(DAT_0052d35c,DAT_0052d080);
              }
            }
            else {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                local_c = DAT_0052d080;
                local_10 = 0x48;
                FUN_0043d574(4,&DAT_0052c920,DAT_0052d088,DAT_0052d084);
              }
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              local_c = DAT_0052d080;
              local_10 = 0x48;
              FUN_0043d574(3,&DAT_0052c920,DAT_0052d088,DAT_0052d084);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            local_c = DAT_0052d080;
            local_10 = 0x48;
            FUN_0043d574(2,&DAT_0052c920,DAT_0052d088,DAT_0052d084);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_c = DAT_0052d080;
          local_10 = 0x48;
          FUN_0043d574(1,&DAT_0052c920,DAT_0052d088,DAT_0052d084);
        }
      }
      attsCheckPendDbHashReadRsp();
    }
    else {
      iVar3 = FUN_004c9c50();
      if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_0052d35c,&DAT_0052c91c,3), iVar3 != 0)) {
        iVar3 = FUN_004c9c50();
        if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_0052d35c,DAT_0052d08c,4), iVar3 != 0)) {
          iVar3 = FUN_004c9c50();
          if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_0052d35c,DAT_0052d35c,4), iVar3 != 0)) {
            iVar3 = FUN_004c9c50();
            if (iVar3 == 0) {
              iVar3 = FUN_004c9c50();
              if ((iVar3 == 0) || (iVar3 = FUN_0044b610(&DAT_0052c920,&DAT_0052c924,3), iVar3 != 0))
              {
                WsfTrace(DAT_0052d35c,DAT_0052d368);
              }
            }
            else {
              iVar3 = FUN_0043d0ce();
              if (iVar3 << 0x1e < 0) {
                local_c = DAT_0052d368;
                local_10 = 0x55;
                FUN_0043d574(4,&DAT_0052c920,DAT_0052d088,DAT_0052d084);
              }
            }
          }
          else {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              local_c = DAT_0052d368;
              local_10 = 0x55;
              FUN_0043d574(3,&DAT_0052c920,DAT_0052d088,DAT_0052d084);
            }
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            local_c = DAT_0052d368;
            local_10 = 0x55;
            FUN_0043d574(2,&DAT_0052c920,DAT_0052d088,DAT_0052d084);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_c = DAT_0052d368;
          local_10 = 0x55;
          FUN_0043d574(1,&DAT_0052c920,DAT_0052d088,DAT_0052d084);
        }
      }
      for (bVar1 = 0; bVar1 < 3; bVar1 = bVar1 + 1) {
        if (*(char *)(iVar2 + (uint)bVar1 * 2 + 1) == '\x02') {
          *(undefined1 *)(iVar2 + (uint)bVar1 * 2 + 1) = 1;
        }
      }
    }
  }
  return CONCAT44(local_c,local_10);
}

