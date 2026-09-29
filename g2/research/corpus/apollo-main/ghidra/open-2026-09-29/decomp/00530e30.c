
undefined4
attcSendSimpleReq(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  
  puVar1 = (undefined2 *)param_1[2];
  param_1[2] = 0;
  if (*(char *)((int)param_1 + 6) != '\n') {
    *(undefined1 *)((int)param_1 + 0x22) = 0x14;
    WsfTimerStartSec(param_1 + 6,*(undefined1 *)(*DAT_00531aac + 6));
  }
  attL2cDataReq(*param_1,*(undefined1 *)((int)param_1 + 0xe),*puVar1,puVar1);
  return param_4;
}

