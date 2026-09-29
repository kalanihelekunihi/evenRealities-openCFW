
undefined4 case_wire_exchange_register(int param_1,undefined4 param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int local_30;
  undefined4 local_2c;
  int iStack_24;
  undefined4 local_20;
  int iStack_1c;
  int local_18;
  
  iVar1 = DAT_0800041c;
  local_2c = 1;
  *(undefined4 *)(DAT_0800041c + 8) = 0;
  if (param_1 << 0x19 < 0) {
    *(undefined4 *)(iVar1 + 8) = 0x1f;
  }
  else {
    iStack_24 = param_1;
    local_20 = param_2;
    iStack_1c = param_3;
    local_18 = param_4;
    case_pulse8_double_train();
    case_pulse8_extended();
    case_emit_bits_alt(param_1,1);
    case_route_boolean_alt(0);
    iVar2 = case_transform_word_alt(&local_30);
    if (iVar2 == 0) {
      case_pulse8_extended();
      uVar3 = 0x20;
    }
    else {
      iVar2 = case_parity8_alt(param_1 * 2 & 0xff);
      if (iVar2 == local_30) {
        case_emit_bits_alt(local_20,0);
        iVar2 = case_transform_word_alt(&local_30);
        if (iVar2 == 0) {
          case_pulse8_extended();
          uVar3 = 0x22;
        }
        else {
          iVar2 = case_parity8_alt(local_20);
          if (iVar2 == local_30) {
            case_pulse8_extended();
            case_emit_bits_alt(param_1,1);
            case_route_boolean_alt(1);
            iVar2 = case_transform_word_alt(&local_30);
            if (iVar2 == 0) {
              case_pulse8_extended();
              uVar3 = 0x24;
            }
            else {
              iVar2 = case_parity8_alt(param_1 * 2 + 1U & 0xff);
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
                uVar3 = 0x26;
              }
              else {
                case_pulse8_extended();
                uVar3 = 0x25;
              }
            }
          }
          else {
            case_pulse8_extended();
            uVar3 = 0x23;
          }
        }
      }
      else {
        case_pulse8_extended();
        uVar3 = 0x21;
      }
    }
    *(undefined4 *)(iVar1 + 8) = uVar3;
  }
  return 0;
}

