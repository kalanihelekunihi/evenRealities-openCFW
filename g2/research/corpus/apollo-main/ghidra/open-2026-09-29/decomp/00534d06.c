
undefined4 attsDiscBusy(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  
  puVar1 = DAT_00535460;
  if (*(int *)*DAT_00535460 != 0) {
    DmConnSetIdle(*(undefined1 *)(*(int *)(param_1 + 0x10) + 0xe),4,1);
    *(undefined1 *)(param_1 + 0x20) = *(undefined1 *)(DAT_00535464 + 0x60);
    *(undefined1 *)(param_1 + 0x1e) = 0x20;
    *(ushort *)(param_1 + 0x1c) = (ushort)*(byte *)(*(int *)(param_1 + 0x10) + 0xe);
    WsfTimerStartSec(param_1 + 0x14,*(undefined4 *)*puVar1);
  }
  return param_4;
}

