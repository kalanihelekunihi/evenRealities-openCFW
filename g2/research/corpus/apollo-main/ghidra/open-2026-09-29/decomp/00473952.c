
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_00473952(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_004742f8;
  uVar1 = osThreadNew(0x473c45,0,PTR_DAT_004742fc);
  *(undefined4 *)(iVar2 + 8) = uVar1;
  if (*(int *)(iVar2 + 8) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 100;
      param_2 = PTR_s__DISP_ThreadInit_osThreadNew_fai_00474300;
      FUN_0043d574(1,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,PTR_s_Disp_ThreadInit_00474304,
                   100,PTR_s__DISP_ThreadInit_osThreadNew_fai_00474300,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__task_displaydrvmgr__DISP_Thread_00474310);
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_1 = 0x66;
      param_2 = PTR_s__DISP_ThreadInit_osThreadNew_0x__00474314;
      FUN_0043d574(4,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,PTR_s_Disp_ThreadInit_00474304,
                   0x66,PTR_s__DISP_ThreadInit_osThreadNew_0x__00474314,*(undefined4 *)(iVar2 + 8),
                   param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,_DAT_00474478,_DAT_00474478,*(undefined4 *)(iVar2 + 8));
    }
  }
  return CONCAT44(param_2,param_1);
}

