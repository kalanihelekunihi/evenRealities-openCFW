
undefined4 case_prepare_controller_context(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 != (int *)0x0) {
    if (param_1[0x22] == 0) {
      *(undefined1 *)(param_1 + 0x21) = 0;
      case_configure_resource_irq(param_1);
    }
    param_1[0x22] = 0x24;
    *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffffe;
    iVar1 = FUN_08008bd8(param_1);
    if (iVar1 != 1) {
      if (param_1[10] != 0) {
        case_apply_context_options(param_1);
      }
      *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xffffb7ff;
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffffd5;
      *(uint *)*param_1 = *(uint *)*param_1 | 1;
      uVar2 = case_wait_controller_channels(param_1);
      return uVar2;
    }
  }
  return 1;
}

