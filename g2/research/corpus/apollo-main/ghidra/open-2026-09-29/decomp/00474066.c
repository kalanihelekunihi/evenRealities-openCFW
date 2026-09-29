
undefined4
FUN_00474066(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
            undefined4 param_5,undefined4 param_6)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 uStack_24;
  
  uStack_24 = param_4;
  FUN_0043c0e4(&local_48,0x24,0);
  local_48 = 3;
  local_34 = param_5;
  local_30 = param_6;
  local_44 = param_1;
  local_40 = param_2;
  local_3c = param_3;
  local_38 = param_4;
  iVar1 = osMessageQueuePut(*(undefined4 *)(DAT_004742f8 + 0xc),&local_48,0,1000);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_00474500,0x161,DAT_004744fc)
      ;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_00474504,DAT_00474504);
    }
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

