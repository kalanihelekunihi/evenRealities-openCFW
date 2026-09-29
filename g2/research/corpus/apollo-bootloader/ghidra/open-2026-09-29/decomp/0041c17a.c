
int FUN_0041c17a(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint *puVar2;
  int iVar3;
  int iVar4;
  uint local_28;
  uint *local_24;
  uint local_20;
  undefined4 local_1c;
  undefined4 local_18;
  uint local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  iVar3 = FUN_0041b8f8(&local_24,param_1);
  if (iVar3 == 0) {
    if ((*local_24 & local_20) == 0) {
      iVar3 = 0;
    }
    else {
      if (param_1 == 0x1d) {
        if (((*DAT_0041cb04 & 0xff) < 0x22) && (*DAT_0041c4ac << 10 < 0)) {
          return 3;
        }
        local_28 = 1;
        iVar4 = delay_us_status_check(DAT_0041cb0c,DAT_0041cb08,1,0);
        iVar3 = 0;
        if (iVar4 != 0) {
          return iVar4;
        }
      }
      if (param_1 == 0x1c) {
        *DAT_0041cb10 = *DAT_0041cb10 & 0xfeffffff;
        puVar2 = DAT_0041cb14;
        *DAT_0041cb14 = *DAT_0041cb14 & 0xfffffffe;
        *puVar2 = *puVar2 & 0xfffffff1;
      }
      FUN_0041cd34();
      local_14 = critical_save();
      *local_24 = *local_24 & ~local_20;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_14 & 1) == 1);
      }
      iVar4 = FUN_0041c0be(param_1);
      if (iVar4 != 0) {
        local_28 = 0;
        iVar3 = delay_us_status_check(5,local_1c,local_18,local_18);
        if (iVar3 == 0) {
          if (param_1 == 0x17) {
            clock_release(4,0x17);
          }
          if (param_1 == 0x14) {
            local_28 = local_28 & 0xffffff00;
            if (*DAT_0041c48c == '\x03') {
              FUN_0041bae8(0);
              *DAT_0041ca08 = 3;
            }
            else {
              *DAT_0041ca08 = 0;
            }
            FUN_0041cd1a(1,1,&local_28);
            FUN_004223d8(0x14);
          }
          else {
            if ((param_1 < 0x1e) && ((local_20 & 0x3fffffff) != 0)) {
              FUN_0041cd1a(3,0,&local_18);
            }
            if ((0x1d < param_1) && ((local_20 & 0x4c4) != 0)) {
              FUN_0041cd1a(4,0,&local_18);
            }
          }
        }
      }
      FUN_0041cd4a();
    }
  }
  return iVar3;
}

