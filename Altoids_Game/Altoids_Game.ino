#include <Adafruit_GFX.h>
#include <Adafruit_SSD1331.h>
#include <SPI.h>
#include <SD.h>
#include <string.h>

// Pins to control the screen
#define sclk 13
#define mosi 11
#define cs   10
#define rst  9
#define dc   8

// Hex values for different colors
#define BLACK           0x0000
#define BLUE            0x001F
#define RED             0xF800
#define GREEN           0x07E0
#define CYAN            0x07FF
#define MAGENTA         0xF81F
#define YELLOW          0xFFE0
#define WHITE           0xFFFF
#define sdcs   4
#define sprite_size 25

// Creating a display
File dataFile;
Adafruit_SSD1331 display = Adafruit_SSD1331(&SPI, cs, dc, rst);

// Booleans for shooting mechanics 
bool shoot = false;
bool isShot = false;

// Time and score
int t = 0;
int score = 0;

// Pins for the two buttons 
int button_1 = 6;
int button_2 = 7;

// Function to draw the sprites pixel by pixel
void drawSprite(int x, int y, int l, int w, uint16_t charmap[]) {
  display.setAddrWindow(0, 0, 96, 64);
  int x_org = x;
  int scalar = 0;
  //This will iterate through the array of hex values and write Pixels according to the color
  for (int i = 0; i < l; i++) {
    display.writePixel(x + (i - (scalar * w) + 1), y, charmap[i]);
    if ((i + 1) % w == 0) {
      x = x_org;
      y += 1;
      scalar += 1;
    }
  }
  display.endWrite();
}

// Universal Class which all entities draw from
class Component {
  public:
    // Position and velocities
    int x, y, x_vel, y_vel;
    // Other state variables
    int current_time, type, delay_time;
    bool dead;
    // Current direction 
    char direct;
    // The positions of the sprite data in the SD card 
    int sprite_pos[8] = {0, 0, 0, 0, 0, 0, 0, 0};
    // Default sprite 
    uint16_t sprite[sprite_size] = {BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK};
    // Arrays read from the SD card that determine the components behavior 
    int parameters[3] = {0, 0, 0};
    int functions[2] = {0, 0};
    int enabled = 0;
    // All other components besides the current component 
    Component * others;
    // Initialization function 
    void initiate(int delay_t, int x_in, int y_in, Component * comps) {
      direct = 'U';
      delay_time = delay_t;
      x = x_in;
      y = y_in;
      others = comps;
    }
    // Sets the current time 
    void settime() {
      current_time = millis();
    }
    // Moves the component using the joystick 
    void joystick() {
      // UP
      if (analogRead(A1) < 100 && analogRead(A0) > 100 && analogRead(A0) < 1000) {
        x_vel = 0;
        y_vel = -1;
        direct = 'U';
      }
      // DOWN
      else if (analogRead(A1) > 1000 && analogRead(A0) > 100 && analogRead(A0) < 1000) {
        x_vel = 0;
        y_vel = 1;
        direct = 'D';
      }
      // LEFT
      else if (analogRead(A0) < 100 && analogRead(A1) > 100 && analogRead(A1) < 1000) {
        x_vel = -1;
        y_vel = 0;
        direct = 'L';
      }
      // RIGHT
      else if (analogRead(A0) > 1000 && analogRead(A1) > 100 && analogRead(A1) < 1000) {
        x_vel = 1;
        y_vel = 0;
        direct = 'R';
      }
      // LEFT UP
      else if (analogRead(A1) < 100 && analogRead(A0) < 100) {
        x_vel = -1;
        y_vel = -1;
        direct = '1';
      }
      // LEFT DOWN
      else if (analogRead(A1) > 1000 && analogRead(A0) < 100) {
        x_vel = -1;
        y_vel = 1;
        direct = '2';
      }
      // RIGHT UP
      else if (analogRead(A1) < 100 && analogRead(A0) > 1000) {
        x_vel = 1;
        y_vel = -1;
        direct = '3';
      }
      // RIGHT DOWN
      else if (analogRead(A1) > 1000 && analogRead(A0) > 1000) {
        x_vel = 1;
        y_vel = 1;
        direct = '4';
      }
      // NO MOVEMENT 
      else {
        x_vel = 0;
        y_vel = 0;
      }
      updatesprite();
    }
    // The component will follow the target 
    void follow() {
      Component target = others[parameters[0]];
      if (!dead) {
        // UP 
        if ((x + 3) == (target.x + 3) && (y + 3) > (target.y + 3)) {
          x_vel = 0;
          y_vel = -1;
          direct = 'U';
        }
        // DOWN
        else if ((x + 3) == (target.x + 3) && (y + 3) < (target.y + 3)) {
          x_vel = 0;
          y_vel = 1;
          direct = 'D';
        }
        // LEFT 
        else if ((x + 3) > (target.x + 3) && (y + 3) == (target.y + 3)) {
          x_vel = -1;
          y_vel = 0;
          direct = 'L';
        }
        // RIGHT
        else if ((x + 3) < (target.x + 3) && (y + 3) == (target.y + 3)) {
          x_vel = 1;
          y_vel = 0;
          direct = 'R';
        }
        // LEFT UP
        else if ((x + 3) > (target.x + 3) && (y + 3) > (target.y + 3)) {
          x_vel = -1;
          y_vel = -1;
          direct = '1';
        }
        // LEFT DOWN 
        else if ((x + 3) > (target.x + 3) && (y + 3) < (target.y + 3)) {
          x_vel = -1;
          y_vel = 1;
          direct = '2';
        }
        // RIGHT UP 
        else if ((x + 3) < (target.x + 3) && (y + 3) > (target.y + 3)) {
          x_vel = 1;
          y_vel = -1;
          direct = '3';
        }
        // RIGHT DOWN
        else if ((x + 3) < (target.x + 3) && (y + 3) < (target.y + 3)) {
          x_vel = 1;
          y_vel = 1;
          direct = '4';
        }
      }
    }
    // Calls the behavior functions as defined by the data from the SD card 
    void callFunctions() {
      if (enabled == 1) {
        if (functions[0] == 1) {
          joystick();
        }
        if (functions[1] == 1) {
          follow();
        }
      }
    }
    // Opens the SD card and reads the sprite values from the given position 
    void pixelAdjust(int pos) {
      char pixel;
      dataFile = SD.open("/datalog.txt");
      dataFile.seek(pos);
      for (int i = 0; i < sprite_size; i++) {
        pixel = dataFile.read();
        if (pixel == 'b') {
          sprite[i] = BLACK;
        }
        if (pixel == 'B') {
          sprite[i] = BLUE;
        }
        if (pixel == 'w') {
          sprite[i] = WHITE;
        }
        if (pixel == 'r') {
          sprite[i] = RED;
        }
        if (pixel == 'g') {
          sprite[i] = GREEN;
        }
        if (pixel == 'c') {
          sprite[i] = CYAN;
        }
        if (pixel == 'm') {
          sprite[i] = MAGENTA;
        }
        if (pixel == 'y') {
          sprite[i] = YELLOW;
        }
      }
      Serial.println();
      dataFile.close();
    }
    // Updates the sprite based on the direction the component is facing 
    void updatesprite() {
      digitalWrite(cs, HIGH);
      digitalWrite(sdcs, LOW);
      if (direct == 'U') {
        pixelAdjust(sprite_pos[0]);
      }
      if (direct == 'D') {
        pixelAdjust(sprite_pos[1]);
      }
      if (direct == 'L') {
        pixelAdjust(sprite_pos[2]);
      }
      if (direct == 'R') {
        pixelAdjust(sprite_pos[3]);
      }
      if (direct == '1') {
        pixelAdjust(sprite_pos[4]);
      }
      if (direct == '2') {
        pixelAdjust(sprite_pos[5]);
      }
      if (direct == '3') {
        pixelAdjust(sprite_pos[6]);
      }
      if (direct == '4') {
        pixelAdjust(sprite_pos[7]);
      }
      // Moves the component based on the delay time for the component 
      if (millis() % delay_time == 0) {
        x += x_vel;
        y += y_vel;
      }
      digitalWrite(sdcs, HIGH);
      digitalWrite(cs, LOW);
      drawSprite(x, y, 25, 5, sprite);
    }
    //void directional() {

    //}
};
Component object[5];

// Function for reading the SD card and assigning behavoir to each component 
void SDread() {
  int i = 0;
  char temp[2] = {0,0};
  int initial[3] = {0,0,0};
  dataFile = SD.open("/datalog.txt");
  if (dataFile) {
    while (dataFile.available()) {
      int pos = dataFile.position();
      char data = dataFile.read();
      // This will initialize and enable the component with the conditions given 
      if (data == '!') {
       for(int k =0; k<3; k++){
        for (int j = 0; j < 2; j++) {
          temp[j] = dataFile.read();
        }
        initial[k] = atoi(temp);
      }
        object[i].enabled = 1;
        object[i].initiate(initial[0],initial[1],initial[2],object);
      }
      // This will allow the component to be controlled by the joystick 
      else if (data == '#') {
        object[i].functions[0] = 1;
      }
      // This will allow the component to follow a target component 
      else if (data == '$') {
        object[i].functions[1] = 1;
        for (int j = 0; j < 2; j++) {
          temp[j] = dataFile.read();
        }
         object[i].parameters[0] = atoi(temp);
      }
      // Gets the positions of each directional sprite in the SD card 
      else if (data == 13) {
        for(int j = 0; j<8; j++){
          object[i].sprite_pos[j] = pos+((sprite_size+2)*j+2);
        }
        dataFile.seek((sprite_size+2)*8 + 2); // Size of sprites * number of sprites + 4
        i++;
      }
    }
    dataFile.close();
  }
}
void setup() {
  Serial.begin(9600);
  pinMode[cs, OUTPUT];
  pinMode[sdcs, OUTPUT];
  display.begin();
  SD.begin(sdcs);
  digitalWrite(sdcs, HIGH);
  digitalWrite(cs, LOW);
  display.fillScreen(BLACK);
  digitalWrite(cs, HIGH);
  digitalWrite(sdcs, LOW);
  SDread();
  digitalWrite(sdcs, HIGH);
  digitalWrite(cs, LOW);
}
void loop() {
  digitalWrite(sdcs, HIGH);
  digitalWrite(cs, LOW);
  display.fillScreen(BLACK);
  digitalWrite(cs, HIGH);
  digitalWrite(sdcs, LOW);
  for(int i=0; i<5; i++){
    object[i].callFunctions();
  }
}
