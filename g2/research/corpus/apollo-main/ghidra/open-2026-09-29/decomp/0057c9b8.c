
int GX8002_SwitchWakeupMode(undefined1 *param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_30 [14];
  undefined1 *local_22;
  short local_1e;
  
  if (param_1 == (undefined1 *)0x0) {
    iVar1 = -1;
  }
  else {
    iVar1 = -1;
    for (iVar3 = 0; iVar3 < 3; iVar3 = iVar3 + 1) {
      FUN_0043c0e4(auStack_30,0x1a,0);
      iVar1 = gx8002_send_and_wait_response(8,0x100,0,0,0,auStack_30,param_2);
      if (iVar1 == 0) break;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0057d010,DAT_0057d00c,DAT_0057d1c4,0x1d2,DAT_0057d1c0,iVar3 + 1,iVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_0057d1c8,DAT_0057d1c8,iVar3 + 1,iVar1);
      }
      semantic_gx8002_free_message(auStack_30);
    }
    if (iVar1 == 0) {
      if (local_1e == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0057d010,DAT_0057d00c,DAT_0057d1c4,0x1dd,DAT_0057d414,local_1e);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0057d5ac,DAT_0057d5ac,local_1e);
        }
        semantic_gx8002_free_message(auStack_30);
        iVar1 = -1;
      }
      else {
        *param_1 = *local_22;
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0057d010,DAT_0057d00c,DAT_0057d1c4,0x1e2,DAT_0057d40c,*param_1);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0057d410,DAT_0057d410,*param_1);
        }
        semantic_gx8002_free_message(auStack_30);
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}

