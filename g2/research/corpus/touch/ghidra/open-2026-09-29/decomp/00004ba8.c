
uint touch_application_18a8_process(uint param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  if (param_1 < 3) {
    iVar3 = *(int *)(param_2 + 0xc) + param_1 * 0x90;
    if (*(char *)(iVar3 + 0x7b) == '\a') {
      uVar2 = 1;
    }
    else {
      iVar1 = touch_sub_4ade();
      if (iVar1 == 0) {
        uVar2 = 8;
      }
      else {
        touch_state_2902_cap_enabled_object(param_1,param_2);
        uVar2 = touch_application_2638_dispatch(param_1,param_2);
        if (*(char *)(iVar3 + 0x7a) == '\x01') {
          touch_select_28a2_dispatch(iVar3,param_2);
        }
        else {
          uVar2 = uVar2 | 1;
        }
      }
    }
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

