
undefined8 FUN_0800056c(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int local_1c;
  int iStack_18;
  
  iVar1 = DAT_0800060c;
  *(undefined4 *)(DAT_0800060c + 4) = 0;
  if ((int)(param_1 << 0x19) < 0) {
    uVar3 = (param_1 & 0xfffffff0) + param_2;
    local_1c = param_3;
    iStack_18 = param_4;
    case_pulse4_extended();
    case_emit_bits(uVar3 & 0xff,1);
    case_route_boolean(0);
    iVar4 = case_transform_word(&local_1c);
    if (iVar4 == 0) {
      case_pulse4_extended();
      uVar2 = 0x16;
    }
    else {
      iVar4 = case_parity8((uVar3 & 0x7f) << 1);
      if (iVar4 == local_1c) {
        iVar4 = 0;
        while( true ) {
          if (param_3 <= iVar4) {
            case_pulse4_extended();
            return 0x100000001;
          }
          case_emit_bits(*(undefined1 *)(param_4 + iVar4),0);
          iVar5 = case_transform_word(&local_1c);
          if (iVar5 == 0) break;
          iVar5 = case_parity8(*(undefined1 *)(param_4 + iVar4));
          if (iVar5 != local_1c) {
            case_pulse4_extended();
            uVar2 = 0x19;
            goto LAB_080005ee;
          }
          iVar4 = iVar4 + 1;
        }
        case_pulse4_extended();
        uVar2 = 0x18;
      }
      else {
        case_pulse4_extended();
        uVar2 = 0x17;
      }
    }
  }
  else {
    uVar2 = 0x15;
  }
LAB_080005ee:
  *(undefined4 *)(iVar1 + 4) = uVar2;
  return 0x100000000;
}

