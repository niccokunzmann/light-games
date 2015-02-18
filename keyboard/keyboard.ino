



void setup_pins() {
  pinMode(A0, INPUT);
  digitalWrite(A0, HIGH);
  pinMode(A1, INPUT);
  digitalWrite(A1, HIGH);
}

void setup() {
  Serial.begin(9600);
  setup_pins();
}

void loop(){
  
}


