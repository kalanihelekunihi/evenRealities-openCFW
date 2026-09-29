
void hciEvtParseVendorSpec(int param_1,undefined4 param_2,byte param_3)

{
  if ((param_3 != 0) && (param_3 < 2)) {
    FUN_00439be4(param_1 + 4,param_2,param_3);
  }
  return;
}

