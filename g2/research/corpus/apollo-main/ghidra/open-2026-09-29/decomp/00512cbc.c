
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
INP_ThreadInit(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_005134b4;
  uVar1 = osThreadNew(0x512ef1,0,_DAT_005134b8);
  *(undefined4 *)(iVar2 + 8) = uVar1;
  if (*(int *)(iVar2 + 8) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0x71;
      param_2 = _DAT_005134bc;
      FUN_0043d574(1,PTR_s_thread_input_005134c8,DAT_005134c4,_DAT_005134c0,0x71,_DAT_005134bc,
                   param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__thread_input_osThreadNew_fail_005134cc);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x73;
      param_2 = PTR_s_osThreadNew_0x_x__success_005134d0;
      FUN_0043d574(4,PTR_s_thread_input_005134c8,DAT_005134c4,_DAT_005134c0,0x73,
                   PTR_s_osThreadNew_0x_x__success_005134d0,*(undefined4 *)(iVar2 + 8),param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,PTR_s__thread_input_osThreadNew_0x_x__s_005134d4,
                          PTR_s__thread_input_osThreadNew_0x_x__s_005134d4,
                          *(undefined4 *)(iVar2 + 8));
    }
  }
  return CONCAT44(param_2,param_1);
}

