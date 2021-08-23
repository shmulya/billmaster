from modules.math_logic import money_box_counter
from time import sleep
import schedule


if __name__ == '__main__':
    schedule.every().day.at("23:59").do(money_box_counter)
    while True:
        schedule.run_pending()
        sleep(60)
