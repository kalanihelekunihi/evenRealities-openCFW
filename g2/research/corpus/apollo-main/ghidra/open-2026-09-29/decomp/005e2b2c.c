
void smpScActCleanup(undefined4 param_1)

{
  smpActCleanup(param_1);
  SmpScFreeScratchBuffers(param_1);
  return;
}

