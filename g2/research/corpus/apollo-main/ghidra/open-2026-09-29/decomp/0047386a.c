
undefined8 FUN_0047386a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_10;
  
  piVar1 = DAT_0047390c;
  if (*DAT_0047390c == 0) {
    local_10 = DAT_00473910;
    FUN_0044d25c(3,DAT_004738f0,0x131,PTR_s_display_buffer_unlock_0047391c);
  }
  else {
    iVar2 = FUN_00442228();
    local_10 = param_3;
    if (iVar2 == 0) {
      FUN_004417ee(*piVar1,0,0,0);
    }
    else {
      FUN_00441a42(*piVar1,0);
    }
  }
  return CONCAT44(param_4,local_10);
}

