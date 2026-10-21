/* Queue and daemon resume callers target Apollo 0x454dcc.
 * Keep the independently compared pending-tick/list source at that entry. */
#include "../../rtos/resume-ticks/resume.c"

__asm__(".global stock_scheduler_resume\n"
        ".set stock_scheduler_resume, audio_resume_pending_ticks_selected\n"
        ".global audio_aux_resume\n.set audio_aux_resume, audio_resume_pending_ticks_selected\n"
        ".global audio_resume\n.set audio_resume, audio_resume_pending_ticks_selected\n"
        ".global receiver_resume\n.set receiver_resume, audio_resume_pending_ticks_selected\n");
