
void attsProcessDatabaseHashUpdate(int param_1)

{
  short sVar1;
  undefined2 local_20;
  undefined1 local_1e;
  undefined1 local_1d;
  undefined4 local_1c;
  undefined2 local_18;
  undefined2 local_16;
  undefined1 local_14;
  undefined2 local_12;
  undefined1 auStack_10 [4];
  undefined1 auStack_c [4];
  
  local_1e = 0x15;
  local_1d = 0;
  local_20 = 0;
  local_18 = 0x10;
  local_16 = 0;
  local_14 = 0;
  local_12 = 0;
  if (*(int *)(param_1 + 8) != 0) {
    WsfBufFree(*(undefined4 *)(param_1 + 8));
    *(undefined4 *)(param_1 + 8) = 0;
  }
  WStrReverse(*(undefined4 *)(param_1 + 4),0x10);
  local_1c = *(undefined4 *)(param_1 + 4);
  sVar1 = attsFindUuidInRange(1,0xffff,2,DAT_00535468,auStack_c,auStack_10);
  if (sVar1 != 0) {
    AttsRemoveGroup(sVar1,0x10,local_1c);
  }
  attsCsfSetHashUpdateStatus(0);
  (**(code **)(DAT_00535464 + 0x58))(&local_20);
  return;
}

