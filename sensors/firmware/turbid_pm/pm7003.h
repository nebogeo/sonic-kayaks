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

const unsigned int PM7003_STREAM_SIZE=64;
const unsigned int PM7003_STREAM_MAX_MSG_SIZE=64;

const unsigned char PM7003_STREAM_MODE_WAIT=0;
const unsigned char PM7003_STREAM_MODE_APPEND=1;

struct pm7003_stream {
  unsigned char mode;
  unsigned int write_pos;
  unsigned int read_pos;
  unsigned char data[PM7003_STREAM_SIZE];
  unsigned char msg[PM7003_STREAM_MAX_MSG_SIZE];
};
