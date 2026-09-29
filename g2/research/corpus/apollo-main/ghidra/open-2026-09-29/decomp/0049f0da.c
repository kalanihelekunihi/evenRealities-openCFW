
void _EnterState(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f760,0x60,DAT_0049f75c,*DAT_0049f744,param_1,
                 param_4);
  }
  iVar2 = FUN_0043d0ce();
  if (-1 < iVar2 << 0x1f) {
    iVar2 = FUN_0043d0ce();
    if (-1 < iVar2 << 0x1d) goto LAB_0049f13c;
  }
  compress_log_output(0xc800000,DAT_0049f764,DAT_0049f764,*DAT_0049f744,param_1);
LAB_0049f13c:
  pcVar1 = DAT_0049f744;
  *DAT_0049f744 = param_1;
  if (param_1 == '\0') {
    uVar3 = 0;
  }
  else {
    uVar3 = _ring_policy_tick_now();
  }
  *(undefined4 *)(pcVar1 + 4) = uVar3;
  pcVar1[8] = '\0';
  return;
}

