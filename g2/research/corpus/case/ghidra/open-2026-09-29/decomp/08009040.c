
int FUN_08009040(undefined4 param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_080090a0;
  iVar3 = 1;
  do {
    disableIRQinterrupts();
    iVar2 = case_wire_read_register(0x42,param_1,param_2,param_3);
    enableIRQinterrupts();
    if (iVar2 != 0) {
      return iVar2;
    }
    iVar3 = iVar3 + 1;
    *(int *)(iVar1 + 4) = *(int *)(iVar1 + 4) + 1;
  } while (iVar3 != 10);
  for (iVar3 = 0; iVar3 < param_2; iVar3 = iVar3 + 1) {
    *(undefined1 *)(param_3 + iVar3) = 0xff;
  }
  if (*DAT_080090a4 == '\0') {
    g2_log_printf(DAT_080090a8,10,*(undefined4 *)(iVar1 + 8),*(undefined4 *)(iVar1 + 0xc),
                  *(undefined4 *)(iVar1 + 0x10));
  }
  return 0;
}

