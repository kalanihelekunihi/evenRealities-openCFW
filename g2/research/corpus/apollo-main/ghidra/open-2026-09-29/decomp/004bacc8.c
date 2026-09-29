
undefined4 FUN_004bacc8(undefined2 *param_1)

{
  undefined4 unaff_r7;
  
  if (*(char *)(param_1 + 1) == '\0') {
    FUN_004bda34();
  }
  else if (*(char *)(param_1 + 1) == '\x02') {
    DmReadRemoteFeatures((char)*param_1);
  }
  return unaff_r7;
}

