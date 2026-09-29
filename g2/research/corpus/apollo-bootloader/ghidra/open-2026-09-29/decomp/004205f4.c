
int FUN_004205f4(undefined2 param_1,uint param_2,char param_3,int param_4,int param_5)

{
  int iVar1;
  int local_34;
  undefined1 local_2f;
  undefined1 local_2e;
  bool local_2d;
  uint local_2c;
  undefined1 local_28;
  undefined2 local_26;
  undefined1 local_24;
  undefined1 local_23;
  int local_20;
  int iStack_1c;
  
  iStack_1c = param_4;
  FUN_00415ff4(&local_34,0x18);
  if (*DAT_00420874 == 0) {
    iVar1 = 2;
  }
  else if ((param_4 == 0) || (param_5 == 0)) {
    iVar1 = 6;
  }
  else if (param_2 < 0x2000000) {
    local_2e = 0;
    local_2c = param_2;
    if (param_3 == '\0') {
      local_2c = 0;
    }
    local_2d = param_3 != '\0';
    local_28 = 1;
    local_24 = 1;
    local_34 = param_5;
    local_2f = 0;
    local_23 = 0;
    local_26 = param_1;
    local_20 = param_4;
    iVar1 = am_hal_mspi_blocking_transfer(*DAT_00420874,&local_34,DAT_00420f0c);
    if (iVar1 != 0) {
      FUN_00415fae(DAT_00420ff4,param_1,param_2,param_5,iVar1);
    }
  }
  else {
    iVar1 = 5;
  }
  return iVar1;
}

