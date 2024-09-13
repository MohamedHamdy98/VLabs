from UserInputs.get_user_inputs_data import AUDIO_PATH, CHOSEN_BACKGROUND_PATH, CHOSEN_VIDEO_PATH, IMAGE_PATH, TEXT_SCRIPT
from FaceSwap.app import run_face_swap_loacl
from Background.app import run_change_background_local
from LipSync.app import lip_sync




face_swap_output_video = run_face_swap_loacl(TARGET_PATH=CHOSEN_VIDEO_PATH, SOURCE_PATH=IMAGE_PATH)

change_background_output_video = run_change_background_local(face_swap_output_video=face_swap_output_video, background_image=CHOSEN_BACKGROUND_PATH)



final_output_video = lip_sync(face_bg_video=change_background_output_video, translated_audio=AUDIO_PATH, padding=str('0 10 0 0'))