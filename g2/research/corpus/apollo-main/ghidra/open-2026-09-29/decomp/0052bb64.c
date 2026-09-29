
undefined8 attsCccCback(undefined4 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  ushort local_18;
  undefined1 local_16;
  undefined1 uStack_15;
  undefined2 local_14;
  undefined2 local_12;
  undefined1 local_10;
  undefined3 uStack_f;
  undefined4 uStack_c;
  
  uStack_15 = (undefined1)((uint)param_1 >> 0x18);
  local_16 = 0x14;
  local_18 = (ushort)param_1 & 0xff;
  _local_10 = CONCAT31((int3)((uint)param_3 >> 8),param_2);
  local_14 = (undefined2)param_3;
  local_12 = (undefined2)param_4;
  uStack_c = param_4;
  (**(code **)(DAT_0052c674 + 0x10))(&local_18);
  return CONCAT26(local_12,CONCAT24(local_14,CONCAT13(uStack_15,CONCAT12(local_16,local_18))));
}

