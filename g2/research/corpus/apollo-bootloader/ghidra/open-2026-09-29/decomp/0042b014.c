
void spotmgr_state_transition_effects_42b014(char param_1,char param_2)

{
  uint *puVar1;
  
  if (((param_2 == '\x01') && (param_1 == '\x02')) && (*DAT_0042b9c8 == '\0')) {
    *DAT_0042b9e8 = 1;
  }
  puVar1 = DAT_0042b9d0;
  if ((param_2 == '\x01') && (param_1 == '\0')) {
    *DAT_0042b9d0 = *DAT_0042b9d0 & 0xfffeffff;
    *puVar1 = *puVar1 & 0xfffffff7;
    *puVar1 = *puVar1 & 0xffffffbf;
    *DAT_0042b9c8 = '\0';
  }
  return;
}

