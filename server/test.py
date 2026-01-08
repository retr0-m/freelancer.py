
# Instagram testing

from instagram.social_media_manager import InstagramManager

UNAME="_.mett.___"

def test_ig():
    bot = InstagramManager()
    bot.send_proposal_to_user_by_username(UNAME, ["/Users/kali/Desktop/business/new websites side hustle/scripts/automating-website-creation/videos_beta_testing/6 - 400x900/456fb63fa4eb166d28bf808bd81e4c7f.webm"],"https://mett.co")

if __name__ == "__main__":
    test_ig()