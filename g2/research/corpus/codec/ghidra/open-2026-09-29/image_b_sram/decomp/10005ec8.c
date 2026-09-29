
void FUN_10005ec8(void)

{
  uRam00000028 = uRam00000028 & 0xfffffffd | 1;
                    /* WARNING: Could not recover jumptable at 0x10005efc. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)(*(uint *)(PTR_PTR_10005f00 + ((uRam00000004 & 0x3f) >> 4) * 4) & 0xfffffffe))();
  return;
}

