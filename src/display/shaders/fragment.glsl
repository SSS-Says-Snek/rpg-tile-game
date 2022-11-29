#version 330

precision mediump float;
uniform sampler2D Texture;
in vec2 v_text;

out vec3 f_color;
void main() {
  // vec3 sus = texture(Texture, v_text).rgb;
  // float avg = (sus.x + sus.y + sus.z) / 3.0;
  f_color = texture(Texture, v_text).rgb;
  // f_color = vec3(avg, avg, avg);
}