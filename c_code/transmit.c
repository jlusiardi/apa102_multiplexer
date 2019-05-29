#include <stdio.h>
#include <stdlib.h>
#include <wiringPiSPI.h>
#include <wiringPi.h>
#include <time.h>
#include <unistd.h>

float fps = 60.0;
int frames = -1;
int frame = 0;

void send_color(int stripes, int leds, int r, int g, int b) {
  unsigned char buffer[(2+192*12)*4];
  int i = 0;
  // start frame -> 32bit all 0
  buffer[i] = 0; i++;
  buffer[i] = 0; i++;
  buffer[i] = 0; i++;
  buffer[i] = 0; i++;

  int s,l;
  for (s=0; s < stripes; s++){
    for (l=0; l < leds; l++){
      // first led -> 32bit all 1
      buffer[i] = 0b11111111; i++;
      if ((frame % 192) == l) {
        buffer[i] = 0xff; i++;	// blue
      } else {
        buffer[i] = 0x0; i++;	// blue
      }
      buffer[i] = 0; i++;	// green
      buffer[i] = 0; i++;	// red
    }
  }

  // end frame -> all 1
  buffer[i] = 0xFF; i++;
  buffer[i] = 0xFF; i++;
  buffer[i] = 0xFF; i++;
  buffer[i] = 0xFF; i++;

  int status = wiringPiSPIDataRW(0, buffer, i);
  if (status == -1) {
    perror("SPI write failed");
    abort();
  }
}

int main(void)
{
  printf("step 1\n");
  wiringPiSetup();
  
  int fd = wiringPiSPISetup(0, 10000000);
  if (fd == -1) {
    perror("SPI Channel setup failed");
    abort();
  }

  struct timespec start;
  struct timespec end;
  while(frames < 0 || frame < frames) {
    clock_gettime(CLOCK_MONOTONIC_RAW, &start);

    send_color(12,192, (255-frame)%255, frame%255, 0);

    frame++;

    clock_gettime(CLOCK_MONOTONIC_RAW, &end);

    long diff = (end.tv_sec - start.tv_sec) * 1000000 + (end.tv_nsec - start.tv_nsec) / 1000;
    printf("diff %d\n", diff);

    useconds_t toSleep; 
    toSleep = (int) ((1.0/fps)*100000.0 - (diff)/100.0);

    printf("to sleep %d\n", toSleep);
    usleep(toSleep);
  }
}

