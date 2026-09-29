
undefined8 FUN_0041de3c(char param_1,undefined4 *param_2,uint param_3)

{
  bool bVar1;
  undefined4 uVar2;
  uint local_10;
  
  local_10 = param_3;
  if (param_2 == (undefined4 *)0x0) {
    uVar2 = 6;
  }
  else {
    if (param_1 == '\x02') {
      local_10 = critical_save();
      *DAT_0041e1a8 = *param_2;
      *DAT_0041e1ac = param_2[1];
      *DAT_0041e1b0 = param_2[2];
      *DAT_0041e1b4 = param_2[3];
      *DAT_0041e1b8 = param_2[4];
      *DAT_0041e1bc = param_2[5];
      *DAT_0041e1c0 = param_2[6];
      *DAT_0041e1c4 = *param_2;
      *DAT_0041e1c8 = param_2[1];
      *DAT_0041e1cc = param_2[2];
      *DAT_0041e1d0 = param_2[3];
      *DAT_0041e1d4 = param_2[4];
      *DAT_0041e1d8 = param_2[5];
      *DAT_0041e1dc = param_2[6];
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_10 & 1) == 1);
      }
    }
    else if (param_1 == '\0') {
      local_10 = critical_save();
      *DAT_0041e1a8 = *param_2;
      *DAT_0041e1ac = param_2[1];
      *DAT_0041e1b0 = param_2[2];
      *DAT_0041e1b4 = param_2[3];
      *DAT_0041e1b8 = param_2[4];
      *DAT_0041e1bc = param_2[5];
      *DAT_0041e1c0 = param_2[6];
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_10 & 1) == 1);
      }
    }
    else if (param_1 == '\x01') {
      local_10 = critical_save();
      *DAT_0041e1c4 = *param_2;
      *DAT_0041e1c8 = param_2[1];
      *DAT_0041e1cc = param_2[2];
      *DAT_0041e1d0 = param_2[3];
      *DAT_0041e1d4 = param_2[4];
      *DAT_0041e1d8 = param_2[5];
      *DAT_0041e1dc = param_2[6];
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_10 & 1) == 1);
      }
    }
    uVar2 = 0;
  }
  return CONCAT44(local_10,uVar2);
}

