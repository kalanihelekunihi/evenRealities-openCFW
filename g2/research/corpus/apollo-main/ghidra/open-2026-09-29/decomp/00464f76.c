
undefined4
FUN_00464f76(undefined2 param_1,undefined4 param_2,uint param_3,undefined4 param_4,
            undefined4 param_5)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *local_24;
  undefined4 uStack_20;
  
  piVar1 = DAT_004651c0;
  uStack_20 = param_4;
  if (*DAT_004651c0 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004651b8,DAT_004651b4,DAT_00465b0c,0xc0,DAT_004651c4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004651cc,DAT_004651cc);
    }
    uVar3 = 0xffffffff;
  }
  else {
    local_24 = (undefined4 *)0x0;
    local_24 = (undefined4 *)FUN_004646f0(0xc);
    if (local_24 == (undefined4 *)0x0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004651b8,DAT_004651b4,DAT_00465b0c,200,DAT_004651d8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004651dc,DAT_004651dc);
      }
      uVar3 = 0xffffffff;
    }
    else {
      FUN_0043c0e4(local_24,0xc,0);
      uVar3 = FUN_004646f0((param_3 & 0xffff) + 8);
      local_24[2] = uVar3;
      if (local_24[2] == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_004651b8,DAT_004651b4,DAT_00465b0c,0xce,DAT_004651d8);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004651dc,DAT_004651dc);
        }
        file_heap_free(local_24);
        uVar3 = 0xffffffff;
      }
      else {
        *local_24 = param_4;
        *(short *)((int)local_24 + 6) = (short)param_3 + 8;
        *(undefined1 *)local_24[2] = 1;
        *(undefined1 *)(local_24[2] + 1) = 9;
        *(char *)(local_24[2] + 2) = (char)param_1;
        *(char *)(local_24[2] + 3) = (char)((ushort)param_1 >> 8);
        *(char *)(local_24[2] + 4) = (char)param_5;
        *(char *)(local_24[2] + 5) = (char)((uint)param_5 >> 8);
        *(char *)(local_24[2] + 6) = (char)param_3;
        *(char *)(local_24[2] + 7) = (char)(param_3 >> 8);
        FUN_00439be4(local_24[2] + 8,param_2,param_3 & 0xffff);
        *(undefined2 *)(local_24 + 1) = 1;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004651b8,DAT_004651b4,DAT_00465b0c,0xe1,DAT_0046545c,local_24);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_00465460,DAT_00465460,local_24);
        }
        iVar2 = osMessageQueuePut(*piVar1,&local_24,0,2000);
        if (iVar2 == 0) {
          osEventFlagsSet(*DAT_00465470,2);
          uVar3 = 0;
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            FUN_0043d574(2,DAT_004651b8,DAT_004651b4,DAT_00465b0c,0xe4,DAT_00465468,iVar2);
          }
          iVar4 = FUN_0043d0ce();
          if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
            compress_log_output(0x8400000,DAT_0046546c,DAT_0046546c,iVar2);
          }
          file_heap_free(local_24[2]);
          file_heap_free(local_24);
          uVar3 = 0xffffffff;
        }
      }
    }
  }
  return uVar3;
}

