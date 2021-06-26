int ledPin = 2;
int senPin = A0;

int nevents = 11; //how many events to count before computing g (MUST BE ODD NUMBER!!)
int srate = 1;    //milliseconds per sample
const int bufsize = 10; //number of samples averaged for background
  
int val;  //Sensor reading
int bkg;  //Background level
int buf[bufsize]; //Circular buffer of past sensor readings
int i = 0;  //Index for buffer 
bool active = false;  //true when string passes in front of light source 

unsigned long events[50];  //Timestamps of pendulum passes
int count = 0;   //Index for "events" array

float L = 0.500 + 0.0506 + 0.020; //Pendulum length (m)
float T;  //Calculated period
float g;  //Calculated gravitational acceleration
float dL = 0.02; //Uncertainty in length (m)
float dg; //Uncertainty in calculated g value

bool mode = 0;
int calibration = 0;  //Check light levels before collecting data
int measurement = 1;  //Measure pendulum period and calculate g


void setup() { 
  pinMode(2, INPUT);  //LOW=calibration, HIGH=measurement
  pinMode(A0, INPUT); //Measures sensor value
  pinMode(3, OUTPUT); //Calibration mode indicator
  pinMode(4, OUTPUT); //Measurement mode indicator
  digitalWrite(3, HIGH); //Start in calibration mode
  digitalWrite(4, LOW);
  Serial.begin(9600);
  Serial.println("Starting program\n\n\n");
}

float getBackground() {
  //Average previous 9 measurements to find background light levels
  float total = 0;
  for(int j=0; j<bufsize; j++) {
    if(j != i) total += buf[j];
  }
  return total/(bufsize-1);
}

void outputResults() {
  T = (events[nevents-1] - events[0])/1000. / ((nevents-1)/2.); //eg nevents=19 is (19-1)/2 = 9 cycles
  g = 4.0*PI*PI*L/(T*T);
  dg = 4.0*PI*PI*dL/(T*T);
        
  Serial.print("Period: ");
  Serial.print(T);
  Serial.println(" s");
  Serial.print("Calculated gravitational acceleration: ");
  Serial.print(g);
  Serial.print(" +/- ");
  Serial.print(dg);
  Serial.println(" m/s^2\n\n\n");
}

void calibrate() {
  //Print value to monitor on serial plotter
  val = analogRead(A0);
  Serial.println(val);
  delay(srate);
}

void measure() {
  //Read light level into buffer
  val = analogRead(A0);
  buf[i] = val;

  //Wait until buffer is filled before checking for events (50ms margin of error)
  if(millis() > bufsize*srate + 50) {
    //Compare to background
    bkg = getBackground();
    if(!active && bkg-val > 5) {
      active = true;
      events[count] = millis();  //Record event timestamp
      count += 1;
      
      //Serial.print("Event ");
      Serial.print(count);
      //Serial.print("   (");
      Serial.print(",");
      Serial.println(millis());
      //Serial.println(" ms)");
     
      if(count == nevents) {
        outputResults();
        delay(3000);
        Serial.println("Restarting data collection in 1 second");
        delay(1000);
        Serial.println("Collecting data\n");  
        count = 0;
      }  
    }
    else if(active && bkg-val < 5) {
      active = false;
    }
  
    //Update index and wait for next measurement
    i+=1;
    if(i==bufsize) i=0;
    delay(srate);
  }
}

int checkMode() {
  //If the "mode" input pin has changed, update the mode of operation
  if(digitalRead(2)!=mode) {
    if(digitalRead(2)==HIGH) {
      digitalWrite(3, LOW);
      digitalWrite(4, HIGH);
      return 1;
    }
    else if(digitalRead(2)==LOW) {
      digitalWrite(3, HIGH);
      digitalWrite(4, LOW);
      return 0;
    }
  }
  else if(digitalRead(2)==mode) return mode;
  else Serial.println("Problem in 'checkMode' function");
}

void loop() {
  mode = checkMode();
  if(mode==calibration) calibrate(); else
  if(mode==measurement) measure();
  else Serial.println("Mode is undefined");
}
