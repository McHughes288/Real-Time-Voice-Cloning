from raspberry.pi import RaspberryPi
import time

rpi = RaspberryPi()
vc_url = "http://code19.cantabresearch.com:8080/jobs"  # "http://localhost:8080/jobs"
uni_asr_url = "ws://code20.cantabresearch.com:9000/v2"
gpt2_url = "http://code20.cantabresearch.com:5000/tell_a_tale"
reset = None

try:
    rpi.initialise_lcd()
    while True:
        # initialise lcd and welcome message
        rpi.lcd.color = [100, 100, 100]
        rpi.lcd_display("Hackamatics 2019\nVoice Cloning")

        # wait for select button
        while rpi.lcd.select_button == False:
            pass

        # record from microphone
        duration = 8
        recording_path = rpi.record_voice(duration)

        # play recording back
        rpi.play_sound(recording_path)

        # check user wants to continue
        rpi.lcd_display("Are you happy\n with recording?")
        
        while True:
            if rpi.lcd.select_button == True:
                reset = False
                break
            elif rpi.lcd.left_button == True:
                reset = True
                break
        if reset == True:
            continue

        # recording_path = "output/recording_2019-12-06_17.54.37.wav"
        # get text prediction from GPT2
        text = rpi.predict_text_gpt2(gpt2_url, uni_asr_url, recording_path) 
        # text_to_synthesize = "Once upon a time, three people decided to slay a big scary dragon"
        print(text)
        text_to_synthesize = text.split("\n")[2].split(".")[0]
        print(text_to_synthesize)

        

        # clone voice and synthesize text
        output_path = rpi.clone_voice(vc_url, recording_path, text_to_synthesize)

        # play cloned voice back
        rpi.play_sound(recording_path)
        rpi.play_sound(output_path)

        # turn off lcd
        rpi.lcd_display("Thanks for using\n voice cloner!", t=3)
        rpi.reset()
        time.sleep(1)

except Exception as e:
    rpi.reset()
    print("Caught exception: %s" % repr(e))


# from raspberry.pi import RaspberryPi
# rpi = RaspberryPi()
# uni_asr_url = "ws://code20.cantabresearch.com:9000/v2"
# gpt2_url = "http://code20.cantabresearch.com:5000/tell_a_tale"
# recording_path = "output/output_2019-12-06_14.40.52.wav"
# text_to_synthesize = rpi.predict_text_gpt2(gpt2_url, uni_asr_url, recording_path)