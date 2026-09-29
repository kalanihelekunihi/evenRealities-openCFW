
undefined4 state_event_dispatch_42d562(byte param_1,undefined4 param_2,char *param_3)

{
  undefined4 uVar1;
  
  uVar1 = 0;
  if (param_1 == 0) {
    if ((param_3 != (char *)0x0) && (*param_3 == '\x02')) {
      state_event_zero_42cfe0();
    }
  }
  else if (param_1 == 2) {
    uVar1 = state_range_update_42ced8(param_3);
  }
  else if (param_1 < 2) {
    if (*param_3 == '\0') {
      uVar1 = state_register_initialize_42d3bc();
    }
    else {
      uVar1 = state_event_one_value_42d104(*param_3);
    }
  }
  return uVar1;
}

