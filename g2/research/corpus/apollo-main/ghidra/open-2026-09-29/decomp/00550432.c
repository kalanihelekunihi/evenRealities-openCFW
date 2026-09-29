
void FUN_00550432(void)

{
  char *pcVar1;
  int *piVar2;
  int iVar3;
  char local_18;
  char local_17;
  undefined1 local_16;
  
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_00550958,DAT_00550954,DAT_00550ec4,0x2a1,DAT_00550ec0);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_00550ec8,DAT_00550ec8);
  }
  iVar3 = DAT_00550ff4;
  pcVar1 = DAT_00550ecc;
  if (*DAT_00550ecc < '\0') {
    FUN_00551ed8(*(undefined4 *)(DAT_00550ff4 + 0x3c),3);
  }
  else {
    FUN_00441488(*(undefined4 *)((short)*DAT_00550ecc * 0x28 + DAT_00550ff4 + 0x40),0xff,0);
    FUN_00551ed8(*(undefined4 *)(iVar3 + 0x3c),2);
    *pcVar1 = -1;
    *DAT_00550f80 = 0xff;
    *DAT_00550f84 = 0xff;
  }
  *DAT_00550d38 = 0;
  piVar2 = DAT_00550f88;
  if ((*DAT_00550f88 != 0) && (iVar3 = ui_common_api_fn_00509dfa(*DAT_00550f88), iVar3 == 0)) {
    FUN_0043c0e4(&local_18,10,0);
    iVar3 = ui_common_api_fn_00509e14(*piVar2,&local_18,6);
    if (iVar3 < 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_00550958,DAT_00550954,DAT_00550ec4,0x2ec,DAT_00550ffc);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00551230,DAT_00551230);
      }
    }
    else if (local_18 == '\x03') {
      if (local_17 == '\n') {
        FUN_00551240();
      }
      else if (local_17 == 'D') {
        FUN_00550820(1);
      }
      else if (local_17 == 'E') {
        FUN_00550820(0xffffffff);
      }
      else if (local_17 == 'F') {
        FUN_00550968(local_16);
      }
      else if ((local_17 == 'H') && (iVar3 = FUN_0045a568(), iVar3 == 1)) {
        FUN_00464c36(4,0,0,0);
      }
    }
    else if ((local_18 == '\x04') && (local_17 == '\x01')) {
      FUN_005511ce(*DAT_00550ff8);
    }
  }
  return;
}

