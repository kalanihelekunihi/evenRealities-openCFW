
undefined4 case_initialize_peripheral_context(undefined4 *param_1)

{
  if (param_1 == (undefined4 *)0x0) {
    return 1;
  }
  if (*(char *)((int)param_1 + 0x3d) == '\0') {
    *(undefined1 *)(param_1 + 0xf) = 0;
    case_hook_08005c26(param_1);
  }
  *(undefined1 *)((int)param_1 + 0x3d) = 2;
  case_apply_controller_profile(*param_1,param_1 + 1);
  *(undefined1 *)(param_1 + 0x12) = 1;
  *(undefined1 *)((int)param_1 + 0x3e) = 1;
  *(undefined1 *)((int)param_1 + 0x3f) = 1;
  *(undefined1 *)(param_1 + 0x10) = 1;
  *(undefined1 *)((int)param_1 + 0x41) = 1;
  *(undefined1 *)((int)param_1 + 0x42) = 1;
  *(undefined1 *)((int)param_1 + 0x43) = 1;
  *(undefined1 *)(param_1 + 0x11) = 1;
  *(undefined1 *)((int)param_1 + 0x45) = 1;
  *(undefined1 *)((int)param_1 + 0x46) = 1;
  *(undefined1 *)((int)param_1 + 0x47) = 1;
  *(undefined1 *)((int)param_1 + 0x3d) = 1;
  return 0;
}

