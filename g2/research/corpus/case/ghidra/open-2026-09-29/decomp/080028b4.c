
undefined4 case_serial_read_200(undefined4 param_1,int param_2,uint param_3)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  
  *DAT_08002928 = 0;
  case_serial_start();
  case_serial_write_byte(200);
  iVar2 = case_serial_ack_sample();
  if (iVar2 == 0) {
    case_serial_write_byte(param_1);
    iVar2 = case_serial_ack_sample();
    if (iVar2 == 0) {
      case_serial_start();
      case_serial_write_byte(0xc9);
      iVar2 = case_serial_ack_sample();
      if (iVar2 == 0) {
        for (uVar3 = 0; uVar3 < param_3; uVar3 = uVar3 + 1 & 0xffff) {
          uVar1 = case_serial_read_byte();
          *(undefined1 *)(param_2 + uVar3) = uVar1;
          if (uVar3 == param_3 - 1) {
            case_serial_ack();
          }
          else {
            case_serial_preamble();
          }
        }
        case_serial_stop();
        return 1;
      }
    }
  }
  case_serial_stop();
  return 0;
}

