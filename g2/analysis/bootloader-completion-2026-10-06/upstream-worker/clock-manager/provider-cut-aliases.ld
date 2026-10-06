/* TEST/CUT USE ONLY. These aliases branch into the locked bootloader image;
 * they are not source implementations and must never satisfy a full
 * source-build dependency. Use only in a harness that maps the exact image. */
PROVIDE(opencfw_bl_clock_request_id2 = 0x00421bd3);
PROVIDE(opencfw_bl_clock_request_id4 = 0x00421d5f);
PROVIDE(opencfw_bl_clock_request_id5 = 0x00421ebb);
PROVIDE(opencfw_bl_clock_request_id6 = 0x004220b3);
PROVIDE(opencfw_bl_clock_release_id2 = 0x00421ccf);
PROVIDE(opencfw_bl_clock_release_id4 = 0x00421e4b);
PROVIDE(opencfw_bl_clock_release_id5 = 0x00422041);
PROVIDE(opencfw_bl_clock_release_id6 = 0x00422221);
