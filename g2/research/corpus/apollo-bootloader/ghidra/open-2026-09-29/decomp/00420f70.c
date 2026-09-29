
undefined4 FUN_00420f70(uint param_1,int param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  int local_30;
  undefined1 local_2b;
  undefined1 local_2a;
  undefined1 local_29;
  uint local_28;
  undefined1 local_24;
  undefined2 local_22;
  undefined1 local_20;
  undefined1 local_1f;
  int local_1c;
  undefined4 uStack_18;
  
  piVar1 = DAT_00421010;
  if (((*DAT_00421010 == 0) || (param_2 == 0)) || (param_3 == 0)) {
    uVar2 = 6;
  }
  else if (param_1 < 0x2000000) {
    uStack_18 = param_4;
    FUN_0041ff08();
    FUN_00420e8c();
    FUN_004207f4();
    FUN_00415ff4(&local_30,0x18);
    local_2a = 0;
    local_29 = 1;
    local_24 = 1;
    local_22 = 0x6c;
    local_20 = 1;
    local_2b = 0;
    local_1f = 0;
    local_30 = param_3;
    local_28 = param_1;
    local_1c = param_2;
    uVar2 = am_hal_mspi_blocking_transfer(*piVar1,&local_30,DAT_004210c4);
    FUN_0041ff1e();
  }
  else {
    uVar2 = 5;
  }
  return uVar2;
}

