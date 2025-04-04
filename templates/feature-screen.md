# Feature description

This feature adds two visual displays above the existing dials, showing the rocket movement and position. Both screen are elements of the same interface players see, so must be in respective style.

The first screen shows the rocket itself. Use rocket.png. The rocket is always centered in the screen, and turned by angle alpha. The image has two engines. When any of the engine is one(any power), there should be fire under this engine(fire.png). For he left angine, the fire imahe is translated 54px to the right and 660px down from top-left corner of rocket.png. The right engine's fine is translated 165px to the right and 660 down. Make sure to apply rotation to both rocket and fires together, so that they look correct. The total height of rocket plus fire will be 863px, width -- 330px. Make sure this whooe thing is centered in the screen(screen of the interface, not actual user's screen). 

The second screen shows position of rocket with respect to planet's surface. Draw the rocket as a simple triangle in the middle of the screen. Only draw anything on this screen if height(h) is >0. Draw planet 100 pixels below the rocket's triangle. It's radius is 6400000m, so in our units its radius is R=(6400000/h)*100px. respectively, it's center must be R+100px below the rocket. 

# Implementation plan

1. Add two empty screens above current navigation controls in the same style as other controls and gauges.
2. Draw rocket.png and two fire.png's in the correct location on the first screen, and with correct angle.
3. Make sure fire is only visible if repsective engine is on(otherwise display:none)
4. Add triangle(make it red with neon as the style of our game) to the center of the second screen. Make it oriented at angle alpha
5. draw a planet beneath it with center at R+100px below thetriange, where R=(6400000/h)*100px. Make the planet green neon.