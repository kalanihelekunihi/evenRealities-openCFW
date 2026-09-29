
int GX8002_ReadVersion(undefined1 *param_1,undefined4 param_2)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_30 [14];
  undefined1 *local_22;
  ushort local_1e;
  
  if (param_1 == (undefined1 *)0x0) {
    iVar2 = -1;
  }
  else {
    iVar2 = -1;
    for (iVar4 = 0; iVar4 < 3; iVar4 = iVar4 + 1) {
      FUN_0043c0e4(auStack_30,0x1a,0);
      iVar2 = gx8002_send_and_wait_response(2,0x100,0,0,0,auStack_30,param_2);
      if (iVar2 == 0) break;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0057d010,DAT_0057d00c,DAT_0057d008,0x17e,DAT_0057d004,iVar4 + 1,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8800000,DAT_0057d014,DAT_0057d014,iVar4 + 1,iVar2);
      }
      semantic_gx8002_free_message(auStack_30);
    }
    if (iVar2 == 0) {
      if (local_1e < 4) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0057d010,DAT_0057d00c,DAT_0057d008,0x191,DAT_0057d1a0,local_1e);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0057d1a4,DAT_0057d1a4,local_1e);
        }
        semantic_gx8002_free_message(auStack_30);
        iVar2 = -1;
      }
      else {
        *param_1 = *local_22;
        param_1[1] = local_22[1];
        param_1[2] = local_22[2];
        param_1[3] = local_22[3];
        puVar1 = DAT_0057d018;
        *DAT_0057d018 = *param_1;
        puVar1[1] = param_1[1];
        puVar1[2] = param_1[2];
        puVar1[3] = param_1[3];
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0057d010,DAT_0057d00c,DAT_0057d008,0x196,DAT_0057d01c,*param_1,
                       param_1[1],param_1[2],param_1[3]);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x11000000,DAT_0057d020,DAT_0057d020,*param_1,param_1[1],param_1[2],
                              param_1[3]);
        }
        semantic_gx8002_free_message(auStack_30);
        iVar2 = 0;
      }
    }
  }
  return iVar2;
}

