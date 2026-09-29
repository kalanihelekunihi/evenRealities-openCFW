
undefined4 case_guarded_controller_disable(undefined4 *param_1)

{
  uint *puVar1;
  uint uVar2;
  
  if (*(char *)(param_1 + 0x21) != '\x01') {
    *(undefined1 *)(param_1 + 0x21) = 1;
    param_1[0x22] = 0x24;
    puVar1 = (uint *)*param_1;
    uVar2 = *puVar1;
    *puVar1 = *puVar1 & 0xfffffffe;
    param_1[0x19] = 0;
    *(uint *)*param_1 = uVar2 & 0xdfffffff;
    param_1[0x22] = 0x20;
    *(undefined1 *)(param_1 + 0x21) = 0;
    return 0;
  }
  return 2;
}

