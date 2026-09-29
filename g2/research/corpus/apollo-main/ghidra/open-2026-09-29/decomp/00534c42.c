
undefined4 attsMsgCback(undefined2 *param_1)

{
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 1) == ' ') {
    DmConnSetIdle((char)*param_1,4,0);
  }
  else if (*(byte *)(param_1 + 1) < 0x23) {
    (**(code **)(*(int *)(DAT_00535448 + 0x260) + 8))();
  }
  else if (*(char *)(param_1 + 1) == '#') {
    (**(code **)(DAT_00535448 + 0x264))();
  }
  else if (*(char *)(param_1 + 1) == '$') {
    attsProcessDatabaseHashUpdate();
  }
  return unaff_r7;
}

