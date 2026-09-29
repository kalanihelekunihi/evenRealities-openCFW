
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
text_stream_start_animation(undefined4 *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  uStack_10 = param_3;
  uStack_c = param_4;
  if (param_1 != (undefined4 *)0x0) {
    *(undefined1 *)(param_1 + 5) = 0;
    if ((int)param_1[3] < (int)param_1[4]) {
      if (((param_2 != '\0') && (param_1[8] != 0)) &&
         (iVar1 = osMutexAcquire(param_1[8],0xffffffff), iVar1 == 0)) {
        if (param_1[7] == 0) {
          iVar1 = osTimerNew(0x553055,1,param_1,0);
          if (iVar1 == 0) {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uStack_c = _DAT_005533ac;
              uStack_10 = 0x1d9;
              FUN_0043d574(1,DAT_005533b8,DAT_005533b4,_DAT_005533b0);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x4000000,_DAT_005533bc);
            }
            osMutexRelease(param_1[8]);
            goto LAB_0055304e;
          }
          param_1[7] = iVar1;
        }
        else {
          osTimerStop(param_1[7]);
        }
        iVar1 = osTimerStart(param_1[7],param_1[2]);
        if (iVar1 != 0) {
          osTimerDelete(param_1[7]);
          param_1[7] = 0;
        }
        osMutexRelease(param_1[8]);
      }
    }
    else {
      iVar1 = ensure_text_capacity(param_1,param_1,param_1 + 9,param_1[4] + 1);
      if ((iVar1 != 0) && (FUN_0048d540(*param_1,param_1[1]), param_1[6] != 0)) {
        (*(code *)param_1[6])(*param_1);
      }
    }
  }
LAB_0055304e:
  return CONCAT44(uStack_c,uStack_10);
}

