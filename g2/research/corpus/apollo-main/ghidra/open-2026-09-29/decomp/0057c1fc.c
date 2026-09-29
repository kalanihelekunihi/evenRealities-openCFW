
uint gx8002_uart_read_blocking(int param_1,ushort param_2,uint param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  ushort uVar5;
  undefined8 uVar6;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar1 = 0xffffffff;
  }
  else {
    uVar6 = FUN_0058fac8();
    iVar4 = (int)((ulonglong)uVar6 >> 0x20);
    uVar2 = (uint)uVar6;
    uVar1 = 0;
    while ((uVar1 & 0xffff) < 0xe) {
      uVar6 = FUN_0058fac8();
      if (((int)((ulonglong)uVar6 >> 0x20) - iVar4 != (uint)((uint)uVar6 < uVar2)) ||
         (param_3 <= (uint)uVar6 - uVar2)) break;
      iVar3 = FUN_0058fb2a((uVar1 & 0xffff) + param_1,0xe - (uVar1 & 0xffff));
      if (iVar3 < 1) {
        osDelay(1);
      }
      else {
        uVar1 = iVar3 + uVar1;
      }
    }
    if ((uVar1 & 0xffff) < 0xe) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057cb58,0x101,DAT_0057cb54,uVar1 & 0xffff,0xe,
                     param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_0057cb5c,DAT_0057cb5c,uVar1 & 0xffff,0xe);
      }
      uVar1 = 0xffffffff;
    }
    else {
      uVar5 = *(short *)(param_1 + 8) + 0xe;
      if (param_2 < uVar5) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057cb58,0x10b,DAT_0057ccd8,uVar5,param_2,
                       param_4);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0057ccdc,DAT_0057ccdc,uVar5,param_2);
        }
        uVar1 = 0xffffffff;
      }
      else {
        while ((uVar1 & 0xffff) < (uint)uVar5) {
          uVar6 = FUN_0058fac8();
          if (((int)((ulonglong)uVar6 >> 0x20) - iVar4 != (uint)((uint)uVar6 < uVar2)) ||
             (param_3 <= (uint)uVar6 - uVar2)) break;
          iVar3 = FUN_0058fb2a((uVar1 & 0xffff) + param_1,(uint)uVar5 - (uVar1 & 0xffff));
          if (iVar3 < 1) {
            osDelay(1);
          }
          else {
            uVar1 = iVar3 + uVar1;
          }
        }
        if ((uVar1 & 0xffff) < (uint)uVar5) {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057cb58,0x11a,DAT_0057cce0,uVar1 & 0xffff,
                         uVar5);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_0057cce4,DAT_0057cce4,uVar1 & 0xffff,uVar5);
          }
          uVar1 = 0xffffffff;
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057cb58,0x11e,DAT_0057cce8,uVar1 & 0xffff)
            ;
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_0057ce54,DAT_0057ce54,uVar1 & 0xffff);
          }
          uVar1 = uVar1 & 0xffff;
        }
      }
    }
  }
  return uVar1;
}

