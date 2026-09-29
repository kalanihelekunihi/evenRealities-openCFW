
undefined8
td_record_elapsed_get(undefined4 param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  if (param_2 == (int *)0x0) {
    uVar1 = 0;
  }
  else {
    *param_2 = 0;
    iVar2 = td_current_record();
    if (iVar2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar4 = *(uint *)(iVar2 + 0x88);
      if (uVar4 == 0) {
        uVar1 = 0;
      }
      else {
        uVar3 = service_time_rtc_refresh();
        if (uVar3 < uVar4) {
          uVar1 = 0;
        }
        else {
          *param_2 = uVar3 - uVar4;
          uVar1 = 1;
        }
      }
    }
  }
  return CONCAT44(param_4,uVar1);
}

