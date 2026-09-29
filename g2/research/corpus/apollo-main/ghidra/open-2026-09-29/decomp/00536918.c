
undefined8 FUN_00536918(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined2 uStack_10;
  undefined1 local_e;
  undefined1 local_d;
  undefined4 uStack_c;
  
  iVar1 = DAT_00536a14;
  uStack_10 = (undefined2)param_3;
  local_e = (undefined1)((uint)param_3 >> 0x10);
  local_d = (undefined1)((uint)param_3 >> 0x18);
  uStack_c = param_4;
  if ((*(char *)(DAT_00536a14 + 0x18) == '\x03') || (*(char *)(DAT_00536a14 + 0x18) == '\x02')) {
    WsfTimerStop(DAT_00536a14);
    local_e = 0x25;
    local_d = 0;
    (**(code **)(DAT_00536a18 + 8))(&uStack_10);
    *(undefined1 *)(iVar1 + 0x18) = 0;
  }
  FUN_0055ba70();
  return CONCAT44(uStack_c,CONCAT13(local_d,CONCAT12(local_e,uStack_10)));
}

