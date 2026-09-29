
undefined4 case_reset_controller_context(int *param_1)

{
  if (param_1 != (int *)0x0) {
    param_1[0x22] = 0x24;
    *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffffe;
    *(undefined4 *)*param_1 = 0;
    *(undefined4 *)(*param_1 + 4) = 0;
    *(undefined4 *)(*param_1 + 8) = 0;
    case_release_peripheral(param_1);
    param_1[0x24] = 0;
    param_1[0x22] = 0;
    param_1[0x23] = 0;
    param_1[0x1b] = 0;
    param_1[0x1c] = 0;
    *(undefined1 *)(param_1 + 0x21) = 0;
    return 0;
  }
  return 1;
}

