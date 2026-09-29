
int FUN_080090ac(undefined4 param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_08009100;
  iVar3 = 1;
  do {
    disableIRQinterrupts();
    iVar2 = case_wire_exchange_register(2,param_1,param_2,param_3);
    enableIRQinterrupts();
    if (iVar2 != 0) {
      return iVar2;
    }
    *(int *)(iVar1 + 4) = *(int *)(iVar1 + 4) + 1;
    g2_log_printf(DAT_08009104,iVar3,*(undefined4 *)(iVar1 + 8),*(undefined4 *)(iVar1 + 0xc),
                  *(undefined4 *)(iVar1 + 0x10));
    iVar3 = iVar3 + 1;
  } while (iVar3 != 10);
  for (iVar1 = 0; iVar1 < param_2; iVar1 = iVar1 + 1) {
    *(undefined1 *)(param_3 + iVar1) = 0xff;
  }
  return 0;
}

