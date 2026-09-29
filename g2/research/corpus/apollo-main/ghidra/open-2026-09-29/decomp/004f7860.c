
void FUN_004f7860(undefined4 param_1)

{
  if (*DAT_004f81e4 == -1) {
    *DAT_004f81e4 = *DAT_004f7c90 - 1;
    FUN_004f7794(param_1);
  }
  else if (*DAT_004f81e4 == -2) {
    *DAT_004f81e4 = 0;
    FUN_004f7f18(-*DAT_004f7c0c);
    FUN_0044ea04(*DAT_004f8090,0,0);
    FUN_004f7794(param_1);
  }
  else {
    FUN_004f7794(param_1);
  }
  *DAT_004f7c0c = 0;
  return;
}

