
undefined8
tracepoint_resolve_file_name(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = DAT_005ee894;
  iVar1 = FUN_0044a43c(DAT_005ee894);
  if ((param_1 == 0) || (iVar2 = FUN_0044b610(param_1,uVar3,iVar1), iVar2 != 0)) {
    uVar3 = 0;
  }
  else {
    uVar3 = tracepoint_parse_file_sequence(param_1 + iVar1,param_2);
  }
  return CONCAT44(param_4,uVar3);
}

