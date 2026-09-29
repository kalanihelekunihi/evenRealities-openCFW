
int case_program_selector_bank(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined1 local_28 [12];
  byte local_1c [8];
  
  iVar5 = 0;
  iVar1 = case_retry_selector8();
  iVar3 = DAT_08009eb8;
  if (-1 < iVar1) {
    iVar4 = 0;
    iVar1 = -1;
    do {
      iVar2 = case_invoke_byte(iVar4 + 0x10U & 0xff,iVar3 + iVar4);
      if (iVar2 != 0) {
        return -1;
      }
      iVar4 = iVar4 + 1;
    } while (iVar4 < 0x50);
    local_1c[0] = 0x80;
    iVar3 = case_invoke_byte(0xb,local_1c);
    if (iVar3 == 0) {
      local_1c[0] = 0;
      iVar3 = case_invoke_byte(10,local_1c);
      if (iVar3 == 0) {
        local_28[0] = 0x30;
        iVar3 = case_invoke_byte(8);
        if (iVar3 == 0) {
          case_nested_delay(0x15);
          local_28[0] = 0;
          iVar3 = case_invoke_byte(8,local_28);
          if (-1 < iVar3) {
            case_nested_delay(0xb);
            do {
              case_nested_delay(0x65);
              case_invoke_mode_one(0xa7,local_1c);
              if ((local_1c[0] & 0xf) >> 2 == 3) {
                return 0;
              }
              iVar5 = iVar5 + 1;
            } while (iVar5 < 0x32);
            case_retry_selector8();
          }
        }
      }
    }
  }
  return iVar1;
}

