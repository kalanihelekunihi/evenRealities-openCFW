
undefined4 FUN_0054443a(char *param_1,undefined4 param_2,undefined1 *param_3)

{
  uint uVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar1 = FUN_0044a43c(param_2);
  if (uVar1 == (byte)param_1[2]) {
    if (((param_1[1] == '\0') || (*param_1 != '\x02')) ||
       (iVar3 = FUN_0044b610(param_1 + 0x10,param_2), iVar3 != 0)) {
      uVar2 = 0;
    }
    else {
      *param_3 = 1;
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

