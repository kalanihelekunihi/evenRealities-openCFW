
undefined4
am_devices_mspi_init(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  
  *DAT_0059d1cc = param_3;
  *DAT_0059d1dc = param_4;
  uStack_18 = param_4;
  uVar1 = osSemaphoreNew(1,0,0);
  *DAT_0059d164 = uVar1;
  iVar2 = FUN_004c0812(0,&local_28);
  if (iVar2 == 0) {
    iVar2 = FUN_004c26e0(local_28,0,0);
    if (iVar2 == 0) {
      uStack_1c = *(undefined4 *)(DAT_0059d220 + 8);
      local_24 = 0x100;
      local_20 = param_2;
      iVar2 = FUN_004c08a8(local_28,&local_24);
      if (iVar2 == 0) {
        iVar2 = FUN_004c099c(local_28,param_3);
        if (iVar2 == 0) {
          iVar2 = FUN_004c0e1e(local_28);
          if (iVar2 == 0) {
            FUN_004c32b4(0,0);
            iVar2 = am_hal_mspi_interrupt_clear(local_28,0x1a80);
            if (iVar2 == 0) {
              iVar2 = FUN_004c2328(local_28,0x1a80);
              if (iVar2 == 0) {
                NVIC_SetPriority(0x14,4);
                NVIC_EnableIRQ(0x14);
                FUN_004c26e0(local_28,2,1);
                *param_1 = local_28;
                uVar1 = 0;
              }
              else {
                iVar2 = FUN_0043d0ce();
                if (iVar2 << 0x1e < 0) {
                  FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d210,0x16b,DAT_0059d23c);
                }
                iVar2 = FUN_0043d0ce();
                if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                  compress_log_output(0x4000000,DAT_0059d240,DAT_0059d240);
                }
                uVar1 = 0xffffffff;
              }
            }
            else {
              uVar1 = 0xffffffff;
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d210,0x15c,DAT_0059d234);
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x4000000,DAT_0059d238,DAT_0059d238);
            }
            uVar1 = 0xffffffff;
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d210,0x156,DAT_0059d22c);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_0059d230,DAT_0059d230);
          }
          uVar1 = 0xffffffff;
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d210,0x150,DAT_0059d224);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0059d228,DAT_0059d228);
        }
        uVar1 = 0xffffffff;
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d210,0x147,DAT_0059d218);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0059d21c,DAT_0059d21c);
      }
      uVar1 = 0xffffffff;
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d210,0x141,DAT_0059d20c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0059d214,DAT_0059d214);
    }
    uVar1 = 0xffffffff;
  }
  return uVar1;
}

