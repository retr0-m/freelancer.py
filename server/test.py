
# Instagram testing

from instagram.social_media_manager import InstagramManager

UNAME="fellinlovewithterpz_3.0"

def test_ig():
    bot = InstagramManager()
    bot.create_driver()
    bot.login()

    bot.open_user_dm(UNAME)
    bot.start_following_user_by_username(UNAME)
    bot.human_sleep(2,4)
    # bot.open_user_dm(UNAME)
    # bot.upload_file_to_dm(UNAME, "/path/video.mp4")
    # bot.send_message_to_user(UNAME, "Broo?")
    bot.quit()

if __name__ == "__main__":
    test_ig()