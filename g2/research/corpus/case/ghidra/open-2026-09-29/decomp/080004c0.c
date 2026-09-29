
undefined4 case_wire_read_register(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int local_30;
  undefined4 local_2c;
  uint uStack_24;
  int iStack_20;
  int iStack_1c;
  int local_18;
  
  iVar1 = DAT_08000568;
  local_2c = 1;
  *(undefined4 *)(DAT_08000568 + 8) = 0;
  if ((int)(param_1 << 0x19) < 0) {
    uStack_24 = param_1;
    iStack_20 = param_2;
    iStack_1c = param_3;
    local_18 = param_4;
    case_pulse8_double_train();
    case_pulse8_extended();
    uVar5 = (param_1 & 0xfffffff0) + param_2 & 0xff;
    case_emit_bits_alt(uVar5,1);
    case_route_boolean_alt(1);
    iVar2 = case_transform_word_alt(&local_30);
    if (iVar2 == 0) {
      case_pulse8_extended();
      uVar3 = 0x2a;
    }
    else {
      iVar2 = case_parity8_alt(uVar5 * 2 + 1 & 0xff);
      if (iVar2 == local_30) {
        iVar2 = 0;
        while( true ) {
          if (param_3 <= iVar2) {
            case_pulse8_extended();
            return local_2c;
          }
          iVar4 = case_collect_bits(local_18 + iVar2);
          if (iVar4 == 0) break;
          if (iVar2 != param_3 + -1) {
            case_route_parity_alt(*(undefined1 *)(local_18 + iVar2));
          }
          iVar2 = iVar2 + 1;
        }
        case_pulse8_extended();
        uVar3 = 0x2c;
      }
      else {
        case_pulse8_extended();
        uVar3 = 0x2b;
      }
    }
    *(undefined4 *)(iVar1 + 8) = uVar3;
  }
  else {
    *(undefined4 *)(iVar1 + 8) = 0x29;
  }
  return 0;
}

