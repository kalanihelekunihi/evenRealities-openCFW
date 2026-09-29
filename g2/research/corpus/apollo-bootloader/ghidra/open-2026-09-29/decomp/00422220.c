
longlong FUN_00422220(undefined1 param_1,undefined4 param_2,uint param_3)

{
  bool bVar1;
  undefined4 *puVar2;
  int iVar3;
  undefined4 local_10;
  
  iVar3 = FUN_004215dc(6,param_1);
  local_10 = param_3;
  if (iVar3 != 0) {
    local_10 = critical_save();
    FUN_00421632(6,param_1,0);
    iVar3 = FUN_004215ae(6);
    if (iVar3 == 0) {
      *DAT_0042245c = 0;
      puVar2 = DAT_00422460;
      syspll_disable_4273dc(*DAT_00422460);
      syspll_deinitialize_427310(*puVar2);
      *puVar2 = 0;
      if (*DAT_00422430 == '\0') {
        FUN_00421cce(0x35);
      }
      else {
        FUN_00421b5c(0x35);
      }
    }
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((local_10 & 1) == 1);
    }
  }
  return (ulonglong)local_10 << 0x20;
}

