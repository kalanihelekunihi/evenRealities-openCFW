
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 atPsnHandler(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = FUN_0044a43c(param_1);
  if (iVar1 == 0xe) {
    at_core_output(0x5a5824,param_1);
    SVC_NvdbWriteSysData(0,param_1);
  }
  else {
    at_core_output(_DAT_005a5828,0xe);
  }
  at_core_output(_DAT_005a582c);
  return 1;
}

