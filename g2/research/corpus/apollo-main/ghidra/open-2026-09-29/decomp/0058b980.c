
void teleprompt_page_data_set_window
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint local_28;
  uint local_24;
  undefined4 uStack_20;
  
  uStack_20 = param_4;
  iVar1 = page_data_lock();
  iVar2 = DAT_0058bc08;
  if (iVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058bc50,DAT_0058bc4c,DAT_0058bcb8,500,DAT_0058bcb4,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0058bcbc,DAT_0058bcbc,param_1);
    }
  }
  else if (*(int *)(DAT_0058bc08 + 0x5190) == 0) {
    semantic_page_data_unlock();
  }
  else {
    iVar1 = semantic_clamp_window_start(param_1);
    iVar3 = osKernelGetTickCount();
    if ((*(char *)(iVar2 + 0x51a1) == '\0') || (*(int *)(iVar2 + 0x5194) != iVar1)) {
      *(int *)(iVar2 + 0x5194) = iVar1;
      *(undefined1 *)(iVar2 + 0x51a1) = 1;
      *(int *)(iVar2 + 0x519c) = iVar3;
      semantic_ensure_range(&local_24,&local_28);
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0058bc50,DAT_0058bc4c,DAT_0058bcb8,0x212,DAT_0058bcc8,param_1,
                     *(undefined4 *)(iVar2 + 0x5194),local_24,local_28);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xd000000,DAT_0058bccc,DAT_0058bccc,param_1,
                            *(undefined4 *)(iVar2 + 0x5194),local_24,local_28);
      }
      uVar6 = *(int *)(iVar2 + 0x5194) + 3;
      if (*(uint *)(iVar2 + 0x5190) <= uVar6) {
        uVar6 = *(int *)(iVar2 + 0x5190) - 1;
      }
      iVar1 = 0;
      iVar3 = 0;
      for (uVar7 = *(uint *)(iVar2 + 0x5194); uVar8 = local_24, uVar7 <= uVar6; uVar7 = uVar7 + 1) {
        uVar5 = semantic_page_to_slot(uVar7);
        iVar4 = semantic_slot_loaded(uVar5,uVar7);
        if (iVar4 == 0) {
          request_page_data_locked(uVar7,0);
          iVar1 = iVar1 + 1;
        }
      }
      for (; uVar8 <= local_28; uVar8 = uVar8 + 1) {
        if ((uVar8 < *(uint *)(iVar2 + 0x5194)) || (uVar6 < uVar8)) {
          uVar5 = semantic_page_to_slot(uVar8);
          iVar4 = semantic_slot_loaded(uVar5,uVar8);
          if (iVar4 == 0) {
            request_page_data_locked(uVar8,0);
            iVar3 = iVar3 + 1;
          }
        }
      }
      iVar2 = teleprompt_preload_timer_ensure_created();
      if ((iVar2 == 0) && (iVar2 = osTimerStart(*DAT_0058bc18,0x9c4), iVar2 != 0)) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0058bc50,DAT_0058bc4c,DAT_0058bcb8,0x22d,DAT_0058bcd0);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0058bcd4,DAT_0058bcd4);
        }
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0058bc50,DAT_0058bc4c,DAT_0058bcb8,0x230,DAT_0058bcd8,iVar1,iVar3);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc800000,DAT_0058bcdc,DAT_0058bcdc,iVar1,iVar3);
      }
      semantic_page_data_unlock();
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0058bc50,DAT_0058bc4c,DAT_0058bcb8,0x202,DAT_0058bcc0,iVar1,
                     iVar3 - *(int *)(iVar2 + 0x519c));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0xc800000,DAT_0058bcc4,DAT_0058bcc4,iVar1,
                            iVar3 - *(int *)(iVar2 + 0x519c));
      }
      iVar1 = teleprompt_preload_timer_ensure_created();
      if (iVar1 == 0) {
        osTimerStart(*DAT_0058bc18,0x9c4);
      }
      *(int *)(iVar2 + 0x519c) = iVar3;
      semantic_page_data_unlock();
    }
  }
  return;
}

