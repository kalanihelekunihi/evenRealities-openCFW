
void Compute_Round(int param_1,byte param_2)

{
  if (param_2 == 0) {
    *(undefined4 *)(param_1 + 0x23c) = DAT_005f5310;
  }
  else if (param_2 == 2) {
    *(undefined4 *)(param_1 + 0x23c) = DAT_005f5314;
  }
  else if (param_2 < 2) {
    *(undefined4 *)(param_1 + 0x23c) = DAT_005f5304;
  }
  else if (param_2 == 4) {
    *(undefined4 *)(param_1 + 0x23c) = DAT_005f5308;
  }
  else if (param_2 < 4) {
    *(undefined4 *)(param_1 + 0x23c) = DAT_005f530c;
  }
  else if (param_2 == 6) {
    *(undefined4 *)(param_1 + 0x23c) = DAT_005f5318;
  }
  else if (param_2 < 6) {
    *(undefined4 *)(param_1 + 0x23c) = DAT_005f5300;
  }
  else if (param_2 == 7) {
    *(undefined4 *)(param_1 + 0x23c) = DAT_005f531c;
  }
  return;
}

