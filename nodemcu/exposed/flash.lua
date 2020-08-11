
-- use D4
ledPin = 0
-- set mode to output
gpio.mode(ledPin, gpio.OUTPUT)

gpio.write(ledPin, 0)

blinkOn = function()
  ledState = 0;
  gpio.write(ledPin, ledState)
end

blinkOff = function()
  ledState = 1;
  gpio.write(ledPin, ledState)
end

-- blink three times to signal ready
tripleBlink = function()
	tmr.create():alarm(100, tmr.ALARM_SINGLE, blinkOn)
	tmr.create():alarm(200, tmr.ALARM_SINGLE, blinkOff)
	tmr.create():alarm(300, tmr.ALARM_SINGLE, blinkOn)
	tmr.create():alarm(400, tmr.ALARM_SINGLE, blinkOff)
	tmr.create():alarm(500, tmr.ALARM_SINGLE, blinkOn)
	tmr.create():alarm(600, tmr.ALARM_SINGLE, blinkOff)
	tmr.create():alarm(700, tmr.ALARM_SINGLE, blinkOn)
	tmr.create():alarm(800, tmr.ALARM_SINGLE, blinkOff)
end



-- set up long-runnning idle loop
tmr.create():alarm(10000, tmr.ALARM_AUTO, tripleBlink)



