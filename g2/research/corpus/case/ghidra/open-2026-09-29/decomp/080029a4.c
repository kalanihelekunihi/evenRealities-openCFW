
undefined4 case_serial_write_pair_200(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  byte bVar2;
  
  bVar2 = 0;
  *DAT_080029fc = 0;
  do {
    case_serial_start();
    case_serial_write_byte(200);
    iVar1 = case_serial_ack_sample();
    if (iVar1 == 0) break;
    bVar2 = bVar2 + 1;
  } while (bVar2 < 200);
  if (bVar2 != 200) {
    case_serial_write_byte(param_1);
    iVar1 = case_serial_ack_sample();
    if (iVar1 == 0) {
      case_serial_write_byte(param_2);
      iVar1 = case_serial_ack_sample();
      if (iVar1 == 0) {
        case_serial_stop();
        return 1;
      }
    }
  }
  case_serial_stop();
  return 0;
}

