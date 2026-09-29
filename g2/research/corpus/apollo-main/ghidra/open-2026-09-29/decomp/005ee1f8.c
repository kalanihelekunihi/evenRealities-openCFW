
void tracepoint_handle_request_file_name(undefined1 param_1)

{
  undefined1 *puVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    uVar2 = tracepoint_role_char();
    FUN_0043d574(3,DAT_005ee79c,DAT_005ee798,DAT_005eeb7c,0x126,DAT_005eeb78,param_1,uVar2);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    uVar2 = tracepoint_role_char();
    compress_log_output(0xc800000,DAT_005eeb80,DAT_005eeb80,param_1,uVar2);
  }
  ble_state_skip_manual_start(0);
  iVar3 = FUN_0048ec9e();
  if (iVar3 != 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005ee79c,DAT_005ee798,DAT_005eeb7c,300,DAT_005eeb84,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_005eeb88,DAT_005eeb88,iVar3);
    }
  }
  iVar3 = tracepoint_scan_files();
  if (iVar3 != 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_005ee79c,DAT_005ee798,DAT_005eeb7c,0x131,DAT_005eeb8c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_005eeb90,DAT_005eeb90);
    }
  }
  puVar1 = DAT_005eeb60;
  FUN_0043c0e4(DAT_005eeb60,0x206,0);
  *puVar1 = 1;
  puVar1[1] = param_1;
  *(undefined2 *)(puVar1 + 2) = 3;
  uVar2 = tracepoint_role_char();
  iVar3 = DAT_005ee794;
  uVar5 = *(uint *)(DAT_005ee794 + 0x80);
  if (0x10 < uVar5) {
    uVar5 = 0x10;
  }
  *(short *)(puVar1 + 4) = (short)uVar5;
  for (uVar6 = 0; uVar6 < uVar5; uVar6 = uVar6 + 1) {
    tracepoint_format_display_name
              (*(undefined4 *)(iVar3 + uVar6 * 8),uVar2,puVar1 + uVar6 * 0x20 + 6,0x20);
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005eeb7c,0x14b,DAT_005eeb94,uVar6,
                   puVar1 + uVar6 * 0x20 + 6,*(undefined4 *)(iVar3 + uVar6 * 8),
                   *(undefined4 *)(iVar3 + uVar6 * 8 + 4));
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x11000000,DAT_005eeeb4,DAT_005eeeb4,uVar6,puVar1 + uVar6 * 0x20 + 6,
                          *(undefined4 *)(iVar3 + uVar6 * 8),*(undefined4 *)(iVar3 + uVar6 * 8 + 4))
      ;
    }
  }
  iVar3 = FUN_0045a568();
  if (iVar3 == 2) {
    iVar3 = tracepoint_send_to_master(0xb,puVar1);
    if (iVar3 != 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005ee79c,DAT_005ee798,DAT_005eeb7c,0x152,DAT_005eeeb8,iVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005eeebc,DAT_005eeebc,iVar3);
      }
    }
  }
  else {
    *DAT_005eefac = 1;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005ee79c,DAT_005ee798,DAT_005eeb7c,0x157,DAT_005eeec0,uVar5);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005eefb0,DAT_005eefb0,uVar5);
    }
  }
  return;
}

