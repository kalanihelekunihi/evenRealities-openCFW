
undefined4 case_read_stable_u16(undefined4 param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  uint local_18;
  
  local_18 = 0;
  iVar1 = case_run_guarded_status(param_1,&local_18,2);
  if (iVar1 == 0) {
    iVar2 = (local_18 & 0xff) * 0x100 + (local_18 >> 8 & 0xff);
    case_nested_delay(5);
    iVar1 = case_run_guarded_status(param_1,&local_18,2);
    if (iVar1 == 0) {
      if (iVar2 != (local_18 & 0xff) * 0x100 + (local_18 >> 8 & 0xff)) {
        case_nested_delay(5);
        iVar1 = case_run_guarded_status(param_1,&local_18,2);
        if (iVar1 != 0) {
          return 0xffffffff;
        }
        iVar2 = (local_18 & 0xff) * 0x100 + (local_18 >> 8 & 0xff);
      }
      *param_2 = iVar2;
      return 0;
    }
  }
  return 0xffffffff;
}

