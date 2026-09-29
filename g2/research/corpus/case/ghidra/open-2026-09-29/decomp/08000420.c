
undefined4 FUN_08000420(uint param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int local_30;
  undefined4 local_2c;
  uint uStack_24;
  int iStack_20;
  int iStack_1c;
  int local_18;
  
  iVar1 = DAT_080004bc;
  local_2c = 1;
  *(undefined4 *)(DAT_080004bc + 4) = 0;
  if ((int)(param_1 << 0x19) < 0) {
    uStack_24 = param_1;
    iStack_20 = param_2;
    iStack_1c = param_3;
    local_18 = param_4;
    case_pulse4_extended();
    uVar5 = (param_1 & 0xfffffff0) + param_2 & 0xff;
    case_emit_bits(uVar5,1);
    case_route_boolean(1);
    iVar3 = case_transform_word(&local_30);
    if (iVar3 == 0) {
      case_pulse4_extended();
      uVar2 = 0x2a;
    }
    else {
      iVar3 = case_parity8(uVar5 * 2 + 1 & 0xff);
      if (iVar3 == local_30) {
        iVar3 = 0;
        while( true ) {
          if (param_3 <= iVar3) {
            case_pulse4_extended();
            return local_2c;
          }
          iVar4 = case_collect_bits(local_18 + iVar3);
          if (iVar4 == 0) break;
          if (iVar3 != param_3 + -1) {
            case_route_parity(*(undefined1 *)(local_18 + iVar3));
          }
          iVar3 = iVar3 + 1;
        }
        case_pulse4_extended();
        uVar2 = 0x2c;
      }
      else {
        case_pulse4_extended();
        uVar2 = 0x2b;
      }
    }
  }
  else {
    uVar2 = 0x29;
  }
  *(undefined4 *)(iVar1 + 4) = uVar2;
  return 0;
}

