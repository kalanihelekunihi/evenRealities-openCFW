
undefined8 FUN_005bae52(char *param_1,char *param_2,char *param_3,undefined1 *param_4,int param_5)

{
  char *pcVar1;
  int iVar2;
  char *pcVar3;
  char *pcVar4;
  undefined1 *puVar5;
  
  if ((param_4 != (undefined1 *)0x0) && (param_5 != 0)) {
    *param_4 = 0;
    pcVar3 = param_3;
    if ((int)param_3 < 0) {
      pcVar3 = (char *)0x0;
    }
    if (0x3b < (int)pcVar3) {
      pcVar3 = (char *)0x3b;
    }
    puVar5 = param_4;
    pcVar1 = (char *)FUN_005bae2e(param_2);
    pcVar4 = &DAT_005bafb0;
    iVar2 = FUN_0046650c();
    if (iVar2 == 1) {
      if ((int)param_2 % 0x18 < 0xc) {
        pcVar4 = &DAT_005bafb4;
      }
      else {
        pcVar4 = &DAT_005bafb8;
      }
    }
    if ((param_1 == (char *)0x0) || (*param_1 == '\0')) {
      FUN_0044b728(param_4,param_5,DAT_005bbc34,pcVar1,pcVar3,pcVar4,param_3,puVar5);
      param_1 = pcVar3;
      param_2 = pcVar4;
    }
    else {
      FUN_0044b728(param_4,param_5,DAT_005bbaa4,param_1,pcVar1,pcVar3,pcVar4,puVar5);
      param_1 = pcVar1;
      param_2 = pcVar3;
    }
  }
  return CONCAT44(param_2,param_1);
}

