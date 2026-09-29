
undefined8 FUN_00481468(char param_1,undefined4 *param_2,uint param_3)

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
      local_10 = FUN_00473940();
      *DAT_004817d8 = *param_2;
      *DAT_004817dc = param_2[1];
      *DAT_004817e0 = param_2[2];
      *DAT_004817e4 = param_2[3];
      *DAT_004817e8 = param_2[4];
      *DAT_004817ec = param_2[5];
      *DAT_004817f0 = param_2[6];
      *DAT_004817f4 = *param_2;
      *DAT_004817f8 = param_2[1];
      *DAT_004817fc = param_2[2];
      *DAT_00481800 = param_2[3];
      *DAT_00481804 = param_2[4];
      *DAT_00481808 = param_2[5];
      *DAT_0048180c = param_2[6];
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_10 & 1) == 1);
      }
    }
    else if (param_1 == '\0') {
      local_10 = FUN_00473940();
      *DAT_004817d8 = *param_2;
      *DAT_004817dc = param_2[1];
      *DAT_004817e0 = param_2[2];
      *DAT_004817e4 = param_2[3];
      *DAT_004817e8 = param_2[4];
      *DAT_004817ec = param_2[5];
      *DAT_004817f0 = param_2[6];
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_10 & 1) == 1);
      }
    }
    else if (param_1 == '\x01') {
      local_10 = FUN_00473940();
      *DAT_004817f4 = *param_2;
      *DAT_004817f8 = param_2[1];
      *DAT_004817fc = param_2[2];
      *DAT_00481800 = param_2[3];
      *DAT_00481804 = param_2[4];
      *DAT_00481808 = param_2[5];
      *DAT_0048180c = param_2[6];
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((local_10 & 1) == 1);
      }
    }
    uVar2 = 0;
  }
  return CONCAT44(local_10,uVar2);
}

