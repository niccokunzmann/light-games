

#include <RunningMedian.h>

#define SERIAL_IDENTIFIER "Light-Keyboard"

const int number_of_samples = 30;
const int noise_reducing_offset = 4;

class Sensor {
  private:
    int pin;
    RunningMedian* rm;
    int last_sample;
    char key;
    boolean just_released;
    boolean just_pressed;
    boolean is_pressed;
  public:
    Sensor(int pin_number, char key_to_press)  {
      pin = pin_number;
      last_sample = 0;
      just_released = false;
      just_pressed = false;
      is_pressed = false;
      rm = new RunningMedian(number_of_samples);
      key = key_to_press;
      setup();
    }
    
    void addSample(int sample) {
      rm->add(sample);
      last_sample = sample;
    }
    
    void read() {
      addSample(analogRead(pin));
    }
    
    float maximum() {
      return rm->getHighest();
    }
    
    float minimum() {
      return rm->getLowest();
    }
    
    float average() {
      return rm->getAverage();
    }
    
    void setup() {
      pinMode(pin, INPUT);      
      digitalWrite(pin, HIGH);
    }
    
    void update() {
      read();
    }
    
    boolean pressed() {
      return last_sample > average() + noise_reducing_offset;
    }
    
    boolean released() {
      return last_sample < average() - noise_reducing_offset;
    }
    
    boolean was_just_released() {
      return just_released;
    }
    
    boolean was_just_pressed() {
      return just_pressed;
    }
    
    void compute_action() {
      boolean _pressed = pressed();
      boolean _released = released();
      if (_pressed && _released) {
        Serial.println("error - pressed and released at the same time. Code is wrong.");
        return;
      }
      just_pressed = false;
      just_released = false;
      if (_pressed && !is_pressed) {
        is_pressed = true;
        just_pressed = true;
      } else if (_released && is_pressed) {
        just_released = true;
        is_pressed = false;
      }
    }
    
    void debug() {
      if (was_just_pressed()) {
        Serial.print(key);
        Serial.println(" was pressed");
      }
      if (was_just_released()) {
        Serial.print(key);
        Serial.println(" was released");
      }
    }
    
    void act_as_key() {
      compute_action();
      if (was_just_pressed()) {
        Serial.print(key);
        Serial.println("+");
      }
      if (was_just_released()) {
        Serial.print(key);
        Serial.println("-");
      }
    }
    
    
    
};

const int number_of_sensors = 6;
Sensor* sensors[number_of_sensors];

void update_sensors() {
  for (int i = 0; i < number_of_sensors; ++i) {
    sensors[i]->update();
    sensors[i]->act_as_key();
  }
}


void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println(SERIAL_IDENTIFIER);
  
  sensors[0] = new Sensor(A0, '0');
  sensors[1] = new Sensor(A1, '1');
  sensors[2] = new Sensor(A2, '2');
  sensors[3] = new Sensor(A3, '3');
  sensors[4] = new Sensor(A4, '4');
  sensors[5] = new Sensor(A5, '5');

}

long next_update = 0;

void loop(){
 
  if (next_update < millis()) {
    update_sensors();
    next_update = millis() + 20;
  }
}


