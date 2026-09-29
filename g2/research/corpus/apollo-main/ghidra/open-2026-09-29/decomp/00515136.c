
void FUN_00515136(int param_1,undefined4 param_2)

{
  if (param_1 != 0) {
    *(undefined4 *)(param_1 + 0xd8) = param_2;
    return;
  }
  *(uint *)(*DAT_005156ac + 0x80) = *(uint *)(*DAT_005156ac + 0x80) | 1;
  return;
}

