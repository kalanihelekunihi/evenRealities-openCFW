
undefined8
service_ancc_notification_process(int param_1,uint param_2,uint param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 uVar2;
  ushort uVar3;
  int iVar4;
  int iVar5;
  undefined1 local_20;
  undefined1 uStack_1f;
  undefined2 uStack_1e;
  uint local_1c;
  uint local_18;
  undefined4 uStack_14;
  
  local_20 = (undefined1)param_1;
  uStack_1f = (undefined1)((uint)param_1 >> 8);
  uStack_1e = (undefined2)((uint)param_1 >> 0x10);
  local_1c = param_2;
  local_18 = param_3;
  uStack_14 = param_4;
  if ((param_1 == 0) || ((param_2 & 0xffff) == 0)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_1c = DAT_00497d6c;
      local_20 = 0x8f;
      uStack_1f = 1;
      uStack_1e = 0;
      FUN_0043d574(1,DAT_00497d78,DAT_00497d74,DAT_00497d70);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00497d7c);
    }
  }
  else {
    iVar4 = service_ancc_record_allocate();
    if (iVar4 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_1c = DAT_00497d80;
        local_20 = 0x95;
        uStack_1f = 1;
        uStack_1e = 0;
        FUN_0043d574(1,DAT_00497d78,DAT_00497d74,DAT_00497d70);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00497d84,DAT_00497d84);
      }
    }
    else {
      FUN_00439be4(iVar4,param_1,0x2fc);
      *(undefined1 *)(iVar4 + 0x2fc) = 1;
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        local_1c = DAT_00497d88;
        local_20 = 0x9b;
        uStack_1f = 1;
        uStack_1e = 0;
        FUN_0043d574(3,DAT_00497d78,DAT_00497d74,DAT_00497d70);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_00497d8c,DAT_00497d8c);
      }
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        local_18 = iVar4 + 8;
        local_1c = DAT_00497d90;
        local_20 = 0xa1;
        uStack_1f = 1;
        uStack_1e = 0;
        FUN_0043d574(3,DAT_00497d78,DAT_00497d74,DAT_00497d70);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00497d94,DAT_00497d94,iVar4 + 8);
      }
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        local_18 = iVar4 + 0x48;
        local_1c = DAT_00497d98;
        local_20 = 0xa2;
        uStack_1f = 1;
        uStack_1e = 0;
        FUN_0043d574(3,DAT_00497d78,DAT_00497d74,DAT_00497d70);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00497d9c,DAT_00497d9c,iVar4 + 0x48);
      }
      for (uVar3 = 0; uVar3 < 5; uVar3 = uVar3 + 1) {
      }
      FUN_0044a43c(iVar4 + 0x68);
      FUN_0044a43c(iVar4 + 0xa8);
      FUN_0044a43c(iVar4 + 0xe8);
      FUN_0044a43c(iVar4 + 0x2e8);
      iVar4 = service_ancc_state_byte1_get(*(undefined1 *)(iVar4 + 0x2f8));
      if (iVar4 == 1) {
        iVar4 = FUN_00467f08();
        if (iVar4 == 1) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            bVar1 = FUN_00467f08();
            local_18 = (uint)bVar1;
            local_1c = DAT_00497da0;
            local_20 = 0x14;
            uStack_1f = 2;
            uStack_1e = 0;
            FUN_0043d574(2,DAT_00497d78,DAT_00497d74,DAT_00497d70);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            uVar2 = FUN_00467f08();
            compress_log_output(0x8400000,DAT_00497da4,DAT_00497da4,uVar2);
          }
        }
        else {
          iVar4 = settings_get_terminal_mode();
          if (iVar4 == 0) {
            iVar4 = FUN_0045a568();
            if (iVar4 == 1) {
              FUN_0043c0e4(&local_20,6,0);
              iVar4 = FUN_00443484();
              if ((iVar4 == 1) && (iVar4 = FUN_004434d0(4), iVar4 == 1)) {
                local_20 = 4;
                uStack_1f = 1;
                FUN_00464bb2(4,&local_20,6,0);
              }
              else if ((*(char *)(DAT_00497cec + 3) == '\0') ||
                      (((iVar4 = FUN_00443484(), iVar4 == 0 || (iVar4 = FUN_004434b4(), iVar4 == 0))
                       || (iVar4 = FUN_004434d0(1), iVar4 == 1)))) {
                FUN_004e1b28(1);
                local_20 = 1;
                uStack_1f = 3;
                FUN_00464b2e(4,&local_20,6,0);
              }
            }
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              local_1c = DAT_00497da8;
              local_20 = 0x19;
              uStack_1f = 2;
              uStack_1e = 0;
              FUN_0043d574(2,DAT_00497d78,DAT_00497d74,DAT_00497d70);
            }
            iVar4 = FUN_0043d0ce();
            if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_00497dac,DAT_00497dac);
            }
          }
        }
      }
    }
  }
  return CONCAT44(local_1c,CONCAT22(uStack_1e,CONCAT11(uStack_1f,local_20)));
}

