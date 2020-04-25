short swap_endian(short in);

const short pm7003_id=0x4d42;

struct pm7003_command {
  short id;
  unsigned char cmd;
  unsigned char data_h; // never used
  unsigned char data_l;
  short verify; 
};

void pm7003_build_command(pm7003_command *cmd, unsigned char type, unsigned char data);

const unsigned char pm7003_cmd_passive_mode = 0xe2;
const unsigned char pm7003_cmd_change_mode = 0xe1;
const unsigned char pm7003_cmd_sleep = 0xe4;

const unsigned char pm7003_data_passive=0x00;
const unsigned char pm7003_data_active=0x01;
const unsigned char pm7003_data_sleep=0x00;
const unsigned char pm7003_data_wakeup=0x01;

struct pm7003_packet {
  short id;
  short frame_len;
  short pmc_std_1_0;
  short pmc_std_2_5;
  short pmc_std_10_0;
  
  short pmc_env_1_0;
  short pmc_env_2_5;
  short pmc_env_10_0;

  short np_0_3;
  short np_0_5;
  short np_1_0;
  short np_2_5;
  short np_5_0;
  short np_10_0;

  short reserved;
  short checksum;
};

// We need to be careful to process data from the sensor as it's not terribly 
// well documented (not sure about the messages sent back after commands) and 
// reads can happen in the middle of messages.
//
// 1. Take arbitrary data of arbitrary lengths
// 2. When one starts with the id bytes start the stream (state=concat)
// 3. Concatenate all following data into the stream until:
// 3a. New id bytes are found or 
// 3b. 32 bytes is reached 
// 4. Then copy the stream to msg and flag ready for reading

// todo: check the checksum for data messages

const unsigned int PM7003_STREAM_SIZE=32;

typedef struct {
  unsigned char msg_ready;
  unsigned int write_pos;
  unsigned char stream[PM7003_STREAM_SIZE];
  unsigned int msg_size;
  unsigned char msg[PM7003_STREAM_SIZE];
} pm7003_stream;

void pm7003_stream_init(pm7003_stream *s);
unsigned char pm7003_id_check(unsigned char *data, unsigned long data_size);
void pm7003_stream_update(pm7003_stream *s, unsigned char *data, unsigned long data_size);

// Utilities
