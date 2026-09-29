
undefined4 case_guarded_controller_field_high(int *param_1,uint param_2)

{
  uint *puVar1;
  uint uVar2;
  
  if ((char)param_1[0x21] != '\x01') {
    *(undefined1 *)(param_1 + 0x21) = 1;
    param_1[0x22] = 0x24;
    puVar1 = (uint *)*param_1;
    uVar2 = *puVar1;
    *puVar1 = *puVar1 & 0xfffffffe;
    *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0x1fffffff | param_2;
    FUN_0800856c(param_1);
    *(uint *)*param_1 = uVar2;
    param_1[0x22] = 0x20;
    *(undefined1 *)(param_1 + 0x21) = 0;
    return 0;
  }
  return 2;
}

