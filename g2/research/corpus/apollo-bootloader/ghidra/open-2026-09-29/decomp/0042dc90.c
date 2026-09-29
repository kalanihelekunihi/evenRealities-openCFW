
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void vector_handoff_42dc90(int param_1)

{
  _DAT_e000ed08 = param_1;
                    /* WARNING: Could not recover jumptable at 0x0042dca0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (**(code **)(param_1 + 4))();
  return;
}

