
int FUN_00460d6c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  piVar1 = DAT_0046158c;
  iVar4 = *DAT_00461588 * (*DAT_00461590 + -5);
  if (iVar4 < 0) {
    iVar4 = 0;
  }
  iVar3 = *DAT_00461588 * *DAT_0046158c;
  if (iVar4 < *DAT_00461588 * *DAT_0046158c) {
    iVar3 = iVar4;
  }
  if (iVar3 < 0) {
    iVar3 = 0;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004611c0,DAT_004611bc,DAT_00461598,0x1f9,DAT_00461594,param_1,*piVar1,iVar3,
                 iVar4,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x11000000,DAT_0046159c,DAT_0046159c,param_1,*piVar1,iVar3,iVar4);
  }
  return iVar3;
}

