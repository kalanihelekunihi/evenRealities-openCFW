
undefined8 tracepoint_parse_file_sequence(int param_1,int *param_2,undefined4 param_3,int param_4)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  int local_18;
  
  local_18 = param_4;
  if ((param_1 == 0) || (param_2 == (int *)0x0)) {
    uVar1 = 0;
  }
  else {
    uVar2 = FUN_0044a43c(param_1);
    if ((uVar2 < 8) ||
       ((iVar3 = FUN_0044b610(param_1,&DAT_005eddc4,3), iVar3 != 0 ||
        (iVar3 = FUN_0046cacc(param_1 + uVar2 + -4,DAT_005ee78c), iVar3 != 0)))) {
      uVar1 = 0;
    }
    else {
      local_18 = 0;
      iVar3 = FUN_0048d874(param_1 + 3,&local_18,10);
      if ((local_18 == 0) || ((local_18 != param_1 + uVar2 + -4 || (iVar3 == 0)))) {
        uVar1 = 0;
      }
      else {
        *param_2 = iVar3;
        uVar1 = 1;
      }
    }
  }
  return CONCAT44(local_18,uVar1);
}

