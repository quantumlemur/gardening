from machine import Pin, PWM, Signal
from time import sleep, sleep_ms, ticks_add, ticks_diff, ticks_ms

import _thread


class LED:
    def __init__(self, config):
        self.config = config

        self.g_led = Pin(self.config.get("G_LED_PIN"), mode=Pin.OUT, pull=None)
        self.r_led = Pin(self.config.get("R_LED_PIN"), mode=Pin.OUT, pull=None)
        self.b_led = Pin(self.config.get("B_LED_PIN"), mode=Pin.OUT, pull=None)
        self.color_cycle = [(1, 1, 0, 0), (1, 1, 1, 0), (1, 0, 0, 0)]

    def start_fader(self):
        """Starts the RGB LED PWM fader cycle loop"""
        print("start")
        _thread.start_new_thread(self._fade_loop, ())
        print("after")

    def _interpolate_state(self, last_state, next_state):
        """Interpolates and returns a new state between the last and the next one"""
        now = ticks_ms()
        pct = float(ticks_diff(now, last_state[0])) / ticks_diff(
            next_state[0], last_state[0]
        )

        state = (
            now,
            (1 - pct) * last_state[1] + pct * next_state[1],
            (1 - pct) * last_state[2] + pct * next_state[2],
            (1 - pct) * last_state[3] + pct * next_state[3],
        )
        # print(last_state, state, next_state, pct)
        # print((1-pct), (1-pct) * last_state[1], pct, pct * next_state[1])
        return state

    def _update_queue(self, ticks_delta=0):
        """Rolls over the color cycle queue and sets the next RGB state"""
        # print(
        #     "now: {} nextduration: {}".format(ticks_ms(), self.color_cycle[0][0] * 1000)
        # )
        next_ticks = ticks_add(ticks_ms(), self.color_cycle[0][0] * 1000 + ticks_delta)
        # set the next state
        next_rgb_state = (
            next_ticks,
            self.color_cycle[0][1],
            self.color_cycle[0][2],
            self.color_cycle[0][3],
        )
        # rotate the color cycle
        self.color_cycle.append(self.color_cycle.pop(0))
        # print("setting next state: {}".format(next_rgb_state))

        return next_rgb_state

    def _fade_loop(self):
        """Loop (to run on a separate thread) which continually updates the state and LEDs"""
        r_pwm = PWM(self.r_led, freq=1000)
        g_pwm = PWM(self.g_led, freq=1000)
        b_pwm = PWM(self.b_led, freq=1000)

        rgb_state = (0, 0, 0, 0)
        next_rgb_state = (ticks_ms(), 0, 0, 0)
        while True:
            ticks_remaining = ticks_diff(next_rgb_state[0], ticks_ms())
            # print(
            #     "next: {} now: {} remaining: {}".format(
            #         next_rgb_state[0], ticks_ms(), ticks_remaining
            #     )
            # )
            # Roll over to the next element in the cycle
            while ticks_remaining <= 0:
                next_rgb_state = self._update_queue(ticks_delta=ticks_remaining)
                ticks_remaining = ticks_diff(next_rgb_state[0], ticks_ms())
            rgb_state = self._interpolate_state(rgb_state, next_rgb_state)
            # print(rgb_state)
            r_pwm.duty(int(rgb_state[1] * 1023))
            g_pwm.duty(int(rgb_state[2] * 1023))
            b_pwm.duty(int(rgb_state[3] * 1023))
            sleep_ms(50)

    def set_rgb_cycle(self, cycle, instant=False):
        """Sets the LED RGB cycle"""
        self.color_cycle = cycle
        if instant:
            self._update_queue()

    def fade_cycle(self, num_loops):
        r_pwm = PWM(self.r_led, freq=1000)
        g_pwm = PWM(self.g_led, freq=1000)
        b_pwm = PWM(self.b_led, freq=1000)
        for l in range(num_loops):
            for i in range(0, 1023 * 2, 10):
                g = abs(i % 2046 - 1023)
                r = abs(int(i - 1023 * 1 / 3) % 2046 - 1023)
                b = abs(int(i - 1023 * 2 / 3) % 2046 - 1023)

                # print(r, g, b)
                r_pwm.duty(r)
                g_pwm.duty(g)
                b_pwm.duty(b)
                sleep_ms(10)
        r_pwm.deinit()
        g_pwm.deinit()
        b_pwm.deinit()
        self.r_led.off()
        self.g_led.off()
        self.b_led.off()

    def cycle_led(self, num_loops):
        for i in range(num_loops):
            print("green {}".format(self.config.get("G_LED_PIN")))
            self.g_led.on()
            sleep(0.5)
            self.g_led.off()

            print("red {}".format(self.config.get("R_LED_PIN")))
            self.r_led.on()
            sleep(0.5)
            self.r_led.off()

            print("blue  {}".format(self.config.get("B_LED_PIN")))
            self.b_led.on()
            sleep(0.5)
            self.b_led.off()

            sleep(1)

    def fade_thread(self, num_loops):
        _thread.start_new_thread(self.fade_cycle, num_loops)


if __name__ == "__main__":
    from config import Config

    config = Config()

    led = LED(config)
    led.start_fader()