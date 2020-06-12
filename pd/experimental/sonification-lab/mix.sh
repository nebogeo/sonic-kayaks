# demo sounds

# # mix background audio into sonification
# sox -m ../sonifications/for_survey/voice-first.wav bg.wav voice-mixed.wav
# sox -m ../sonifications/for_survey/synth-first.wav bg.wav synth-mixed.wav
# sox -m ../sonifications/for_survey/sample-first.wav bg.wav sample-mixed.wav
# sox -m ../sonifications/for_survey/grain-first.wav bg.wav grain-mixed.wav

# # trim result to 2 minutes
# sox voice-mixed.wav voice-mixed-trim.wav trim 0 02:00
# sox synth-mixed.wav synth-mixed-trim.wav trim 0 02:00
# sox sample-mixed.wav sample-mixed-trim.wav trim 0 02:00
# sox grain-mixed.wav grain-mixed-trim.wav trim 0 02:00

# # insert as audio on video
# ffmpeg -y -i bg_video_sm.mp4 -i voice-mixed-trim.wav -c:v copy -map 0:v:0 -map 1:a:0 voice-first.mp4
# ffmpeg -y -i bg_video_sm.mp4 -i synth-mixed-trim.wav -c:v copy -map 0:v:0 -map 1:a:0 synth-first.mp4
# ffmpeg -y -i bg_video_sm.mp4 -i sample-mixed-trim.wav -c:v copy -map 0:v:0 -map 1:a:0 sample-first.mp4
# ffmpeg -y -i bg_video_sm.mp4 -i grain-mixed-trim.wav -c:v copy -map 0:v:0 -map 1:a:0 grain-first.mp4

# rm voice-mixed.wav voice-mixed-trim.wav
# rm sample-mixed.wav sample-mixed-trim.wav
# rm synth-mixed.wav synth-mixed-trim.wav
# rm grain-mixed.wav grain-mixed-trim.wav

# survey test sounds

# mix background audio into sonification
sox -m ../sonifications/for_survey/voice-survey.wav bg.wav voice-mixed.wav
sox -m ../sonifications/for_survey/synth-survey.wav bg.wav synth-mixed.wav
sox -m ../sonifications/for_survey/sample-survey.wav bg.wav sample-mixed.wav
sox -m ../sonifications/for_survey/grain-survey.wav bg.wav grain-mixed.wav

# trim result to 2 minutes
sox voice-mixed.wav voice-mixed-trim.wav trim 0 00:30
sox synth-mixed.wav synth-mixed-trim.wav trim 0 00:30
sox sample-mixed.wav sample-mixed-trim.wav trim 0 00:30
sox grain-mixed.wav grain-mixed-trim.wav trim 0 00:30

# insert as audio on video
ffmpeg -y -i bg_video_survey.mp4 -i voice-mixed-trim.wav -c:v copy -map 0:v:0 -map 1:a:0 voice-survey.mp4
ffmpeg -y -i bg_video_survey.mp4 -i synth-mixed-trim.wav -c:v copy -map 0:v:0 -map 1:a:0 synth-survey.mp4
ffmpeg -y -i bg_video_survey.mp4 -i sample-mixed-trim.wav -c:v copy -map 0:v:0 -map 1:a:0 sample-survey.mp4
ffmpeg -y -i bg_video_survey.mp4 -i grain-mixed-trim.wav -c:v copy -map 0:v:0 -map 1:a:0 grain-survey.mp4

#ffmpeg -y -i voice-survey-long.mp4 -ss 00:00:15 -to 00:00:45 -c:v copy -c:a copy voice-survey.mp4
#ffmpeg -y -i sample-survey-long.mp4 -ss 00:00:15 -to 00:00:45 -c:v copy -c:a copy sample-survey.mp4
#ffmpeg -y -i synth-survey-long.mp4 -ss 00:00:15 -to 00:00:45 -c:v copy -c:a copy synth-survey.mp4
#ffmpeg -y -i grain-survey-long.mp4 -ss 00:00:15 -to 00:00:45 -c:v copy -c:a copy grain-survey.mp4

rm voice-mixed.wav voice-mixed-trim.wav 
rm sample-mixed.wav sample-mixed-trim.wav
rm synth-mixed.wav synth-mixed-trim.wav
rm grain-mixed.wav grain-mixed-trim.wav


# reduce file size for upload

#ffmpeg -y -i voice-first.mp4 -vf scale=-1:720 voice-first-sm.mp4
#ffmpeg -y -i synth-first.mp4 -vf scale=-1:720 synth-first-sm.mp4
#ffmpeg -y -i sample-first.mp4 -vf scale=-1:720 sample-first-sm.mp4
#ffmpeg -y -i grain-first.mp4 -vf scale=-1:720 grain-first-sm.mp4
#ffmpeg -y -i voice-survey.mp4 -vf scale=-1:720 voice-survey-sm.mp4
#ffmpeg -y -i synth-survey.mp4 -vf scale=-1:720 synth-survey-sm.mp4
#ffmpeg -y -i sample-survey.mp4 -vf scale=-1:720 sample-survey-sm.mp4
#ffmpeg -y -i grain-survey.mp4 -vf scale=-1:720 grain-survey-sm.mp4
