
undefined4 request_page_data_locked(uint param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint local_28;
  undefined4 uStack_24;
  
  iVar3 = DAT_0058b530;
  uStack_24 = param_4;
  if (*(uint *)(DAT_0058b530 + 0x5190) <= param_1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058b538,0x94,DAT_0058b534,param_1,
                   *(int *)(iVar3 + 0x5190) + -1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4800000,DAT_0058b53c,DAT_0058b53c,param_1,*(int *)(iVar3 + 0x5190) + -1)
      ;
    }
    return 0xffffffff;
  }
  iVar1 = semantic_page_to_slot(param_1);
  iVar2 = semantic_slot_loaded(iVar1,param_1);
  if (iVar2 == 0) {
    iVar2 = osKernelGetTickCount();
    if (((*(int *)(iVar1 * 0x414 + iVar3 + 0x410) != 0) &&
        (*(uint *)(iVar3 + iVar1 * 0x414) == param_1)) &&
       ((uint)(iVar2 - *(int *)(iVar1 * 0x414 + iVar3 + 0x410)) < 500)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_28 = iVar2 - *(int *)(iVar1 * 0x414 + iVar3 + 0x410);
        FUN_0043d574(4,DAT_0058b354,DAT_0058b350,DAT_0058b538,0xa3,DAT_0058b548,param_1,iVar1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_0058b54c,DAT_0058b54c,param_1,iVar1,
                            iVar2 - *(int *)(iVar3 + iVar1 * 0x414 + 0x410));
      }
      return 0;
    }
    if ((*(char *)(iVar1 * 0x414 + iVar3 + 0x40c) == '\x01') &&
       (*(uint *)(iVar3 + iVar1 * 0x414) == param_1)) {
      iVar4 = semantic_loading_timed_out(iVar1,param_1,iVar2);
      if (iVar4 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0058b354,DAT_0058b350,DAT_0058b538,0xaa,DAT_0058b550,param_1,iVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc800000,DAT_0058b554,DAT_0058b554,param_1,iVar1);
        }
        return 0;
      }
      uVar5 = iVar2 - *(int *)(iVar1 * 0x414 + iVar3 + 0x410);
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_28 = uVar5;
        FUN_0043d574(2,DAT_0058b354,DAT_0058b350,DAT_0058b538,0xae,DAT_0058b558,param_1,iVar1);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8c00000,DAT_0058b55c,DAT_0058b55c,param_1,iVar1,uVar5);
      }
    }
    else {
      if ((*(char *)(iVar1 * 0x414 + iVar3 + 0x40c) != '\0') &&
         (*(uint *)(iVar3 + iVar1 * 0x414) == param_1)) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          local_28 = (uint)*(byte *)(iVar1 * 0x414 + iVar3 + 0x40c);
          FUN_0043d574(1,DAT_0058b354,DAT_0058b350,DAT_0058b538,0xb4,DAT_0058b838,param_1,iVar1);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4c00000,DAT_0058b954,DAT_0058b954,param_1,iVar1,
                              *(undefined1 *)(iVar3 + iVar1 * 0x414 + 0x40c));
        }
        return 0xffffffff;
      }
      *(undefined1 *)(iVar1 * 0x414 + iVar3 + 0x40c) = 1;
      *(uint *)(iVar3 + iVar1 * 0x414) = param_1;
    }
    local_28 = param_1;
    APP_PbTxEncodePageDataRequest(&local_28);
    *(int *)(iVar3 + iVar1 * 0x414 + 0x410) = iVar2;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0058b354,DAT_0058b350,DAT_0058b538,0xbb,DAT_0058b560,param_1,iVar1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0058b564,DAT_0058b564,param_1,iVar1);
    }
    if (((param_2 != '\0') && (iVar3 = teleprompt_preload_timer_ensure_created(), iVar3 == 0)) &&
       (iVar3 = osTimerStart(*DAT_0058b358,0x9c4), iVar3 != 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0058b354,DAT_0058b350,DAT_0058b538,0xbf,DAT_0058b830,param_1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0058b834,DAT_0058b834,param_1);
      }
    }
    return 0;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0058b354,DAT_0058b350,DAT_0058b538,0x9a,DAT_0058b540,param_1,iVar1);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc800000,DAT_0058b544,DAT_0058b544,param_1,iVar1);
  }
  return 0;
}

