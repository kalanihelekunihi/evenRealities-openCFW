
void touch_pipeline_1ac4_reset_one(int param_1,int param_2,int param_3)

{
  bool bVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_3 + 0xc);
  bVar1 = false;
  while (!bVar1) {
    touch_record_1ab8_reset(*(int *)(iVar2 + param_1 * 0x90 + 4) + param_2 * 10);
    bVar1 = true;
  }
  return;
}

