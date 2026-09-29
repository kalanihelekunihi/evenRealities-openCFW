
undefined8
l2cSlaveReqTimeout(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar1 = FUN_004c9c50();
  local_10 = param_3;
  local_c = param_4;
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00536f7c,&DAT_00536c54,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00536f7c,DAT_00536f7c,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00536f7c,DAT_00536f8c,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&LAB_00536c58,&LAB_00536e9c,3), iVar1 != 0)) {
            WsfTrace(DAT_00536f7c,DAT_00536f80);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            local_c = DAT_00536f80;
            local_10 = 0x4a;
            FUN_0043d574(4,&LAB_00536c58,DAT_00536f88,DAT_00536f84);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          local_c = DAT_00536f80;
          local_10 = 0x4a;
          FUN_0043d574(3,&LAB_00536c58,DAT_00536f88,DAT_00536f84);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_c = DAT_00536f80;
        local_10 = 0x4a;
        FUN_0043d574(2,&LAB_00536c58,DAT_00536f88,DAT_00536f84);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_00536f80;
      local_10 = 0x4a;
      FUN_0043d574(1,&LAB_00536c58,DAT_00536f88,DAT_00536f84);
    }
  }
  DmL2cConnUpdateCnf(*param_1,1);
  return CONCAT44(local_c,local_10);
}

