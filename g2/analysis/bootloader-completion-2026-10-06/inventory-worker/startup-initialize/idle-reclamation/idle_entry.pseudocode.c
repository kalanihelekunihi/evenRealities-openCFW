/* Readable pseudocode, NOT compiled reconstruction.
 * Direct locked bytes4189ac..4189fa; caller4189c0 missing from Ghidra corpus.
 * Official FreeRTOS idle task corroborates call ordering. Units: scheduler ticks.
 */
void idle_task_4189ac(void) {
 for (;;) {
  idle_cleanup_418a98();
  if (*(uint32_t *)0x20024870 >= 2) request_pendsv_41b3d0();
  uint32_t expected = expected_idle_ticks_4181e4();
  if (expected < 2) continue;
  scheduler_suspend_4181d8();
  if (*(uint32_t *)0x20027164 < *(uint32_t *)0x20027148) {
   mask_interrupts_41b2f8();*(uint32_t *)0xffffffff=0;for(;;){}
  }
  expected = expected_idle_ticks_4181e4();
  if (expected >= 2) suppress_ticks_and_sleep_41b754(expected);
  scheduler_resume_418228();
 }
}
