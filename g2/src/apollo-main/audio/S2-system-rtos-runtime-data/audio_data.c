/* Apollo main audio product state: the audio thread-manager record (slot 3,
 * platform/threads/thread_audio.c), the LC3 recording service
 * (a-58-service-audio) and the algorithm energy service (p-10-service-algo).
 * liblc3 state belongs to the upstream liblc3 units.
 *
 * .data values are from the decoded startup init image (RAM
 * 0x20000000..0x20004557); sizes are the sizeof of the referencing
 * declarations and match the gap to the next stock object. */
#include <stdint.h>

/* Thread-manager record {init, deinit, thread, queue} (16 B). */
typedef struct {
    void (*init)(void);   /* +0x0 */
    void (*deinit)(void); /* +0x4 */
    void *thread;         /* +0x8 osThreadId_t */
    void *queue;          /* +0xc osMessageQueueId_t */
} g2_tm_thread_record_t;
_Static_assert(sizeof(g2_tm_thread_record_t) == 16u, "thread manager record");

void AUD_ThreadInit(void);                  /* 0x53c344 */
void audio_thread_terminate_selected(void); /* 0x53c4f2 */

/* RAM 0x20003f98 (.data): init = 0x53c345, deinit = 0x53c4f3, thread and
 * queue created at run time. */
g2_tm_thread_record_t g2_audio_dispatch_state = {AUD_ThreadInit, audio_thread_terminate_selected, 0, 0};

/* RAM 0x200036d0 (.data): recording base names, ROM 0x78be40 / 0x78be4c. */
const char *g2_audio_recording_basenames_200036d0[2] = {"front_mic", "rear_mic"};

uint8_t g2_audio_recording_rows_20073c08[2u * 12u] __attribute__((aligned(4))); /* RAM 0x20073c08 */
volatile uint8_t g2_audio_lc3_packet_seq_2007500e;                             /* RAM 0x2007500e */

/* Algorithm service: 800 stereo pairs split into L/R/front PCM (SSRAM), and
 * 64-bit mean-square energies over a 10-entry window. */
int16_t g2_algo_left_pcm[800];        /* RAM 0x20375400 */
int16_t g2_algo_right_pcm[800];       /* RAM 0x20375a40 */
int16_t g2_algo_front_pcm[800];       /* RAM 0x20376080 */
uint64_t g2_algo_left_energy;         /* RAM 0x20074168 */
uint64_t g2_algo_right_energy;        /* RAM 0x20074170 */
uint64_t g2_algo_window_index;        /* RAM 0x20074178 */
uint64_t g2_algo_energy_window[10];   /* RAM 0x20072d08 */
