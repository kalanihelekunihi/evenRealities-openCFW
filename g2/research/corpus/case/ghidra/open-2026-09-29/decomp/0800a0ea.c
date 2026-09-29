
undefined4 case_retry_selector8(void)

{
  int iVar1;
  
  iVar1 = case_invoke_byte(8);
  if (iVar1 == 0) {
    case_nested_delay(0x15);
    iVar1 = case_invoke_byte(8);
    if (iVar1 == 0) {
      case_nested_delay(0xb);
      return 0;
    }
  }
  return 0xffffffff;
}

