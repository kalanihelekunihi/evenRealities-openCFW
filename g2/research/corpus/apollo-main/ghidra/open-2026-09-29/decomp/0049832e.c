
void service_even_ai_fn_0049832e(uint param_1,int param_2)

{
  byte bVar1;
  undefined1 uVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 uVar7;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  uint uStack_14;
  int local_10;
  
  uStack_14 = param_1;
  local_10 = param_2;
  if ((param_1 & 0xff) == 1) {
    iVar4 = productModeGet();
    if (((((iVar4 == 1) || (iVar4 = semantic_OtaTransferActive(), iVar4 == 1)) ||
         (iVar4 = onboarding_should_run(), iVar4 == 1)) ||
        ((iVar4 = FUN_00467f08(), iVar4 == 1 || (iVar4 = get_silent_mode_ui_showing(), iVar4 == 1)))
        ) || ((local_10 == 0 && (*DAT_004985cc == 1)))) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        uVar5 = semantic_OtaTransferActive();
        bVar1 = productModeGet();
        local_18 = (uint)*DAT_004985cc;
        local_1c = uVar5 & 0xff;
        local_20 = (uint)bVar1;
        local_24 = DAT_004985fc;
        FUN_0043d574(2,DAT_004985bc,DAT_004985b8,DAT_00498600,0x16e);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar2 = semantic_OtaTransferActive();
        uVar3 = productModeGet();
        local_24 = (uint)*DAT_004985cc;
        compress_log_output(0x8c00000,DAT_00498604,DAT_00498604,uVar3,uVar2);
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        uVar5 = get_silent_mode_ui_showing();
        uVar6 = FUN_00467f08();
        local_20 = onboarding_should_run();
        local_18 = uVar5 & 0xff;
        local_1c = uVar6 & 0xff;
        local_24 = DAT_00498608;
        FUN_0043d574(2,DAT_004985bc,DAT_004985b8,DAT_00498600,0x170);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        uVar5 = get_silent_mode_ui_showing();
        uVar2 = FUN_00467f08();
        uVar7 = onboarding_should_run();
        local_24 = uVar5 & 0xff;
        compress_log_output(0x8c00000,DAT_0049860c,DAT_0049860c,uVar7,uVar2);
      }
    }
    else {
      iVar4 = service_even_ai_fn_00497de6();
      if (iVar4 == 0) {
        uVar7 = osKernelGetTickCount();
        *DAT_004985ac = uVar7;
        local_18 = DAT_00498618[2];
        local_20._3_1_ = (undefined1)((uint)*DAT_00498618 >> 0x18);
        local_20._0_3_ = CONCAT12((char)param_1,(short)*DAT_00498618);
        local_1c = CONCAT13(DAT_004985cc[1],(int3)DAT_00498618[1]);
        FUN_00439be4((int)&local_20 + 3,&local_10,4);
        iVar4 = even_ai_scroll_needed();
        if (iVar4 == 0) {
          iVar4 = even_ai_text_stream_service_get();
          local_18 = CONCAT31(local_18._1_3_,*(undefined1 *)(iVar4 + 1));
          iVar4 = even_ai_text_stream_service_get();
          local_18._0_2_ = CONCAT11((char)*(undefined2 *)(iVar4 + 4),(undefined1)local_18);
          iVar4 = even_ai_text_stream_service_get();
          local_18._0_3_ =
               CONCAT12((char)((ushort)*(undefined2 *)(iVar4 + 4) >> 8),(undefined2)local_18);
        }
        FUN_00464f76(7,&local_20,0xb,DAT_0049861c,5);
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_24 = DAT_00498610;
          FUN_0043d574(2,DAT_004985bc,DAT_004985b8,DAT_00498600,0x176);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_00498614,DAT_00498614);
        }
      }
    }
  }
  else if (((param_1 & 0xff) == 3) && (*DAT_004985a8 != '\0')) {
    local_24._3_1_ = (undefined1)((uint)*DAT_00498620 >> 0x18);
    local_24._0_3_ = CONCAT12((char)param_1,(short)*DAT_00498620);
    FUN_00464f76(7,&local_24,3,DAT_0049861c,5);
  }
  return;
}

