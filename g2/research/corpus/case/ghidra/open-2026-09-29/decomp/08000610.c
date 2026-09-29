
undefined8 case_wire_write_register(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  int local_1c;
  int iStack_18;
  
  iVar1 = DAT_080006c0;
  *(undefined4 *)(DAT_080006c0 + 8) = 0;
  if (-1 < (int)(param_1 << 0x19)) {
    *(undefined4 *)(iVar1 + 8) = 0x15;
    return 0x100000000;
  }
  uVar2 = (param_1 & 0xfffffff0) + param_2;
  local_1c = param_3;
  iStack_18 = param_4;
  case_pulse8_double_train();
  case_pulse8_extended();
  case_emit_bits_alt(uVar2 & 0xff,1);
  case_route_boolean_alt(0);
  iVar3 = case_transform_word_alt(&local_1c);
  if (iVar3 == 0) {
    case_pulse8_extended();
    uVar4 = 0x16;
  }
  else {
    iVar3 = case_parity8_alt((uVar2 & 0x7f) << 1);
    if (iVar3 == local_1c) {
      iVar3 = 0;
      while( true ) {
        if (param_3 <= iVar3) {
          case_pulse8_extended();
          return 0x100000001;
        }
        case_emit_bits_alt(*(undefined1 *)(param_4 + iVar3),0);
        iVar5 = case_transform_word_alt(&local_1c);
        if (iVar5 == 0) break;
        iVar5 = case_parity8_alt(*(undefined1 *)(param_4 + iVar3));
        if (iVar5 != local_1c) {
          case_pulse8_extended();
          uVar4 = 0x19;
          goto LAB_080006a0;
        }
        iVar3 = iVar3 + 1;
      }
      case_pulse8_extended();
      uVar4 = 0x18;
    }
    else {
      case_pulse8_extended();
      uVar4 = 0x17;
    }
  }
LAB_080006a0:
  *(undefined4 *)(iVar1 + 8) = uVar4;
  return 0x100000000;
}

