
undefined4 event_dispatch_42f38e(byte param_1,undefined4 param_2,char *param_3)

{
  if (param_1 != 0) {
    if (param_1 == 2) {
      *(undefined4 *)(param_3 + 4) = DAT_0042f62c;
      *(undefined4 *)(param_3 + 8) = DAT_0042f630;
    }
    else if (param_1 < 2) {
      if (*param_3 == '\0') {
        hw_register_profile_restore_42f2fa();
      }
      else {
        event_value_profile_42f204(*param_3);
      }
    }
  }
  return 0;
}

