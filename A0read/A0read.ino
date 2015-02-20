

#define SERIAL_IDENTIFIER "Light-Keyboard"

const int number_of_samples = 30;
const int noise_reducing_offset = 20;

class Sensor {
  private:
    int pin;
    int last_sample;
    int reference_sample;
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
      key = key_to_press;
      setup();
    }
    
    int last_sensor_value() {
      return last_sample;
    }
    
    void addSample(int sample) {
      last_sample = sample;
    }
    
    void read() {
      addSample(analogRead(pin));
    }

    void setup() {
      pinMode(pin, INPUT);      
      digitalWrite(pin, HIGH);
    }
    
    void update() {
      read();
    }
    
    boolean pressed() {
      return reference_sample + noise_reducing_offset < last_sample;
    }
    
    boolean released() {
      return reference_sample - noise_reducing_offset > last_sample;
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
      if (_pressed || _released) {
        reference_sample = last_sample;
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

void print_sensor_values() {
  for (int i = 0; i < number_of_sensors - 1; ++i) {
    int sensor_value = sensors[i]->last_sensor_value();
    Serial.print(sensor_value);
    Serial.print("\t");
  }
  if (number_of_sensors > 1) {
    int sensor_value = sensors[number_of_sensors - 1]->last_sensor_value();
    Serial.println(sensor_value);  
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
 update_sensors();
 if (Serial.available()) {
   int inByte = Serial.read();
   print_sensor_values();
 }
}


