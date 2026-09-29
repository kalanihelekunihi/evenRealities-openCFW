
longlong FUN_0041d9aa(uint param_1,byte param_2,uint param_3)

{
  bool bVar1;
  undefined4 local_10;
  
  local_10 = param_3;
  if (param_2 == 0) {
    *(int *)(DAT_0041e128 + ((param_1 & 0xff) >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  else if (param_2 == 2) {
    local_10 = critical_save();
    *(uint *)(DAT_0041e120 + ((param_1 & 0xff) >> 5) * 4) =
         1 << (param_1 & 0x1f) ^ *(uint *)(DAT_0041e120 + ((param_1 & 0xff) >> 5) * 4);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  else if (param_2 < 2) {
    *(int *)(DAT_0041e12c + ((param_1 & 0xff) >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  else if (param_2 == 4) {
    *(int *)(DAT_0041e134 + ((param_1 & 0xff) >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  else if (param_2 < 4) {
    *(int *)(DAT_0041e130 + ((param_1 & 0xff) >> 5) * 4) = 1 << (param_1 & 0x1f);
  }
  else if (param_2 == 5) {
    local_10 = critical_save();
    *(uint *)(DAT_0041e124 + ((param_1 & 0xff) >> 5) * 4) =
         1 << (param_1 & 0x1f) ^ *(uint *)(DAT_0041e124 + ((param_1 & 0xff) >> 5) * 4);
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

