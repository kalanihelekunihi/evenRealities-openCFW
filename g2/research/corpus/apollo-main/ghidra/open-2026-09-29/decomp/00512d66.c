
undefined8
INP_ResourceInit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_005134b4;
  uVar1 = osMessageQueueNew(0x1e,0xc,0);
  *(undefined4 *)(iVar2 + 0xc) = uVar1;
  if (*(int *)(iVar2 + 0xc) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x7b;
      param_2 = DAT_005134d8;
      FUN_0043d574(1,PTR_s_thread_input_005134c8,DAT_005134c4,DAT_005134dc,0x7b,DAT_005134d8,param_3
                   ,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005134e0);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x7d;
      param_2 = DAT_005134e4;
      FUN_0043d574(4,PTR_s_thread_input_005134c8,DAT_005134c4,DAT_005134dc,0x7d,DAT_005134e4,
                   *(undefined4 *)(iVar2 + 0xc),param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005134e8,DAT_005134e8,*(undefined4 *)(iVar2 + 0xc));
    }
  }
  return CONCAT44(param_2,param_1);
}

