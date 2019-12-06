from raspberry.pi import RaspberryPi

rpi = RaspberryPi()
vc_url = "http://code19.cantabresearch.com:8080/jobs"  # "http://localhost:8080/jobs"
gpt2_url = None

try:
    rpi.initialise_lcd()

    # TODO while True, wait for button press

    rpi.lcd_display("Hackamatics 2019\nVoice Cloning", t=5)

    duration = 10
    recording_path = rpi.record_voice(duration, playback=True)

    text_to_synthesize = rpi.predict_text_gpt2(gpt2_url, recording_path)

    rpi.clone_voice(vc_url, recording_path, text_to_synthesize)

except Exception as e:
    rpi.reset()
    print("Caught exception: %s" % repr(e))
