
undefined4 profileAnccConnOpenAdapter(undefined1 param_1,undefined4 param_2)

{
  undefined1 *puVar1;
  undefined4 unaff_r7;
  
  puVar1 = DAT_004bf6c0;
  *DAT_004bf6c0 = param_1;
  *(undefined4 *)(puVar1 + 4) = param_2;
  _anccResetStateMachine();
  return unaff_r7;
}

