from raspberry.pi import RaspberryPi
import threading

rpi = RaspberryPi()
vc_url = "http://code19.cantabresearch.com:8080/jobs"  # "http://localhost:8080/jobs"
gpt2_url = None

try:
    rpi.initialise_lcd()

    while True:
        reset = False
        # welcome message
        rpi.lcd_display("Hackamatics 2019\nVoice Cloning")

        # wait for select button
        while rpi.lcd.select_button == False:
            pass

        # record from microphone
        duration = 5
        recording_path = rpi.record_voice(duration)

        # play recording back
        rpi.play_sound(recording_path)

        # check user wants to continue
        rpi.lcd_display("Are you happy\n with recording?")
        while True:
            if rpi.lcd.select_button == True:
                break
            elif rpi.lcd.left_button == True:
                reset = True
                break
        if reset == True:
            continue

        # get text prediction from GPT2
        text_to_synthesize = rpi.predict_text_gpt2(gpt2_url, recording_path)

        # clone voice and synthesize text
        output_path = rpi.clone_voice(vc_url, recording_path, text_to_synthesize)

        # play cloned voice back
        rpi.play_sound(recording_path)
        rpi.play_sound(output_path)

        # turn off lcd
        rpi.lcd_display("Thanks for using\n voice cloning!", t=3)
        rpi.reset()

except Exception as e:
    rpi.reset()
    print("Caught exception: %s" % repr(e))
