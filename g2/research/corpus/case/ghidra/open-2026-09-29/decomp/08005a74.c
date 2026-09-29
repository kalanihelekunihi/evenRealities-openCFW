
int case_activate_controller(int *param_1)

{
  int iVar1;
  
  if (param_1 == (int *)0x0) {
    return 1;
  }
  if (*(char *)((int)param_1 + 0x29) == '\0') {
    *(undefined1 *)(param_1 + 10) = 0;
    param_1[1] = 0x8800;
    case_configure_controller_irq(param_1);
  }
  *(undefined1 *)((int)param_1 + 0x29) = 2;
  if ((int)(~*(uint *)(*param_1 + 0xc) << 0x1b) < 0) {
    *(undefined4 *)(*param_1 + 0x24) = 0xca;
    *(undefined4 *)(*param_1 + 0x24) = 0x53;
    iVar1 = case_wait_controller_ready(param_1);
    if (iVar1 == 0) {
      *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & DAT_08005b20;
      *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | param_1[2] | param_1[5] | param_1[7]
      ;
      *(int *)(*param_1 + 0x10) = param_1[4];
      *(uint *)(*param_1 + 0x10) =
           *(uint *)(*param_1 + 0x10) | (uint)*(ushort *)(param_1 + 3) << 0x10;
      iVar1 = case_prepare_controller_wait(param_1);
      if (iVar1 == 0) {
        *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0x1fffffff;
        *(uint *)(*param_1 + 0x18) =
             *(uint *)(*param_1 + 0x18) | param_1[9] | param_1[8] | param_1[6];
      }
    }
    *(undefined4 *)(*param_1 + 0x24) = 0xff;
    if (iVar1 != 0) {
      return iVar1;
    }
  }
  *(undefined1 *)((int)param_1 + 0x29) = 1;
  return 0;
}

