# Game description

This is a collaborative educational game where my students are going to collaborate to simultenously control a rocket. It's a real time online game. All players(students) see the same thing and have access to the same shared controls. The interface is in Ukrainian language.

# Stack

Use HTML and JS for frontend, Python(Flask+Socket.io) for backend

# Parameters

Game is purely parametric, it's state depends on parameters:

1. Висота ракети над рівнем моря(h, in 0)
2. Тиск атмосфери(p = 1-h/100000, min 0)
3. Вертикальна швидкість(v_y += ((e_l+e_r)*cos(alpha)-10)*dt)
4. Горизонтальна швидкість(v_x += (e_l+e_r)*sin(alpha)*dt)
5. Кут ракети відносно землі(alpha+(e_l-e_r)*dt mod 360)
6. Кількість палива в двигуні(f=1000-(e_r+e_l)*dt, min 0)
7. Кількість залишившихся стадій ракети(ns=5, min 0)
8. Потужність лівого двигуна(e_l, range 0 to 5)
9. Потужність правого двигуна(e_r, range 0 to 5)
10. Температура корпусу ракети(t += (sqrt(v_x^2 + v_y^2)*p-1)*dt, min 0)
11. Температиура лівого двигуна(t_l += (e_l-1)*dt, min 0)
12. Температура правого двигуна(t_r += (e_r-1)*dt, min 0)
13. Рівень заряду батареї(c=1000-0.5dt+sp*dt, min 0)
14. Температура батареї(t_c=0 + sp*dt-0.75dt, min 0)
15. Стан сонячних панелей(sp, 0 or 1)
16. Рівень звʼязку(ls=1-(mu_in-mu_r)^2/mu_r^2*dt+dt, max 1)
17. Частота вхідного сигналу(mu_in=100 += randint(-1 to 1)*dt with 1% chance per each tick)
18. Частота приймача(mu_r=100)
19. Плин часу з одним ігровим тіком(dt=1, 10 ticks per second)

# Initial Conditions

- Starting height (h) = 0 (launch from sea level)
- Initial left engine power (e_l) = 0
- Initial right engine power (e_r) = 0
- Solar panels initially closed (sp = 0)

# Controls

Players have access  to the following controls

1. Підвищити потужність лівого двигуна(e_l+=1)
2. Понизити потужність лівого двигуна(e_l-=1)
3. Підвищити потужність правого двигуна(e_r+=1)
4. Понизити потужність правого двигуна(e_r-=1)
5. Відкрити/закрити сонячні панелі(sp = 1-sp)
6. Підвищити частоту приймача(mu_r+=1)
7. Понизити частоту приймача(mu_r-=1)
8. Відʼєднати стадію ракети(n-=1, f=1000)

# Interface

Players all share a common interface, where there is a bunch of gauges showing various values and buttons for all the controls. All players can press all the buttons. Use reference.html and reference.css for example of styles for gauges and buttons, and make somehting similar.

Make sure the layout is responsive, as some of the players may conect with mobile devices. 

The interface should show the number of currently connected players.

When the game is lost, a game over screen should be displayed with a message and a restart option.

# Game rules
The game is lost if:

1. h=0 and v_y<10(but make sure that initially the game is not lost in the first tick, we need some time to launch)
2. Any temperature reaches 1000(temp gauges show range 0 to 1000)

The goal of the game is to launch and survive as long as possible. 

# Implementation plan

Your goal is to implement the game in these steps. Make sure you read the description carefuly and you understand everything in it. If something is not 100% clear, ask me about it.

If you ready, implement the first step and then let me check everything before we move to step 2.

1. Create a flask server, allowing players to connect simultaneously.
2. Add game loop on the server. It should be based on socket.io functionality so that other processes do not interrupt it. Add display to frontend that will display the number of ticks passed. This display should be updated with each tick, by a new socket sent from server to client.
3. Add a new variable "counted ticks" that will be updated together with server ticks, and add a pause/play button that will turn running them on or off. Notice that this button should not start nor stop the server timer -- it should work forever with no interuptions at all. Only the new secondary timer is affected by it.
4. Add logic for the game. Implement all the variables and processes specified in this file. Make simple logging for them on the frontend, just so that I see that they are there and something is happening. 
5. Add gauges and buttons for all parameters and controls using simple style(so that if there is any bug, it's surely not due to styling)
6. Implement styles similar to reference.html and reference.css. Also, please make the layout more reasonable, locate butttons close to gauges of parameters they affect. Remove tick counters and headins from the game. Make overall look fitting to the reference style files.


# Additional Notes

- Game timing: Exactly 100ms between ticks (10 ticks per second)
- No player identification required, only show total number of connected players
- No visual representation of the rocket in the initial implementation (may be added later)
- No save/load functionality - game state resets when server restarts
- Statistics tracking (highest altitude, longest survival time) may be added in future iterations
- Server should run on port 5001, not 5000. I have another process there.
- Command for running python is 'python3' in my setup.