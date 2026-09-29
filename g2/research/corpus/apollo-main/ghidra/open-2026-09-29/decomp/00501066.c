
void FUN_00501066(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined1 local_1c;
  undefined1 local_1b;
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  iVar2 = FUN_0045a568();
  if (iVar2 == 2) {
    cVar1 = FUN_0055876a();
    FUN_0043c0e4(&local_1c,6,0);
    local_1c = 3;
    local_1b = cVar1 != '\0';
    if (param_1 != '\0') {
      FUN_00454b4c(100);
    }
    FUN_00465480(0x1f,&local_1c,6,0,5);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00501188,DAT_00501184,DAT_00501818,0x1f1,DAT_00501814,cVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,PTR_s__dashboard_ext_dashboard_ext__sl_00501d0c,
                          PTR_s__dashboard_ext_dashboard_ext__sl_00501d0c,cVar1);
    }
  }
  return;
}

