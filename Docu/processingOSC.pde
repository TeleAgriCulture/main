import oscP5.*;
import netP5.*;

OscP5 oscP5;

// latest values
float BPM = 0;
float temp = 0;
float hum = 0;

float acc_X = 0;
float acc_Y = 0;
float acc_Z = 0;

String lastAddress = "";

void setup() {
  size(1000, 600);

  // must match OSC Port configured in TeleAgriCulture
  oscP5 = new OscP5(this, 9000);

  textSize(18);

  println("Listening for TeleAgriCulture OSC on port 9000");
}

void draw() {
  background(20);

  fill(255);

  text("TeleAgriCulture OSC Monitor", 20, 30);
  text("Last OSC Address: " + lastAddress, 20, 60);

  text("Temperature: " + nf(temp, 0, 2) + " °C", 20, 120);
  text("Humidity: " + nf(hum, 0, 2) + " %", 20, 150);
  text("Heartbeat: " + nf(BPM, 0, 2), 20, 180);

  // Heartbeat visualization
  float pulse = map(BPM, 0, 100, 40, 200);

  fill(255);
  ellipse(180, 320, pulse, pulse);

  // Gyroscope visualization
  pushMatrix();

  translate(width * 0.7, height * 0.5);

  rotate(radians(acc_Z));

  rectMode(CENTER);

  noFill();
  stroke(255);
  strokeWeight(3);

  rect(0, 0, 150, 150);

  popMatrix();

  fill(255);

  text("acc_X: " + nf(acc_X, 0, 2), width-250, 120);
  text("acc_Y: " + nf(acc_Y, 0, 2), width-250, 150);
  text("acc_Z: " + nf(acc_Z, 0, 2), width-250, 180);
}


void oscEvent(OscMessage msg) {

  if (msg.typetag().length() == 0)
    return;

  float value = msg.get(0).floatValue();

  String addr = msg.addrPattern();

  lastAddress = addr;

  println(addr + " : " + value);

  // match measurement name only
  if (addr.endsWith("/BPM")) {
    heartbeat = value;
  }
  else if (addr.endsWith("/temp")) {
    temp = value;
  }
  else if (addr.endsWith("/hum")) {
    hum = value;
  }
  else if (addr.endsWith("/acc_x")) {
    acc_X = value;
  }
  else if (addr.endsWith("/acc_y")) {
    acc_Y = value;
  }
  else if (addr.endsWith("/acc_z")) {
    acc_Z = value;
  }
}
