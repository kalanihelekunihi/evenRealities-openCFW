
int FUN_08009108(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_08009160;
  iVar3 = 1;
  do {
    disableIRQinterrupts();
    iVar2 = case_wire_write_register(0x42,param_1,param_2,param_3);
    enableIRQinterrupts();
    if (iVar2 != 0) {
      return iVar2;
    }
    iVar3 = iVar3 + 1;
    *(int *)(iVar1 + 4) = *(int *)(iVar1 + 4) + 1;
  } while (iVar3 != 10);
  if (*DAT_08009164 == '\0') {
    g2_log_printf(DAT_08009168,10,*(undefined4 *)(iVar1 + 8),*(undefined4 *)(iVar1 + 0xc),
                  *(undefined4 *)(iVar1 + 0x10));
    g2_log_printf(&DAT_0800916c);
  }
  return 0;
}

