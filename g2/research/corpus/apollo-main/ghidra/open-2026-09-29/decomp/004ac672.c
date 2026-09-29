
void FUN_004ac672(char param_1)

{
  int iVar1;
  undefined1 local_14;
  undefined1 local_13;
  char local_12;
  undefined1 local_11;
  undefined1 local_d;
  
  FUN_0043c0e4(&local_14,8,0);
  local_12 = FUN_0045a568();
  local_14 = 4;
  local_13 = 1;
  if (local_12 == '\x01') {
    local_11 = 2;
  }
  else {
    local_11 = 1;
  }
  local_d = param_1 == '\0';
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,DAT_004acda8,0x1b6,DAT_004acda4,param_1);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_004acdac,DAT_004acdac,param_1);
  }
  FUN_00464f76(0x81,&local_14,8,0,5);
  return;
}

