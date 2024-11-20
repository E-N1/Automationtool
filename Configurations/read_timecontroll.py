from dotenv import load_dotenv
import os


class ReadTimecontroll():
    load_dotenv()

    def getCurrentStatus(self, masch):
        """
        Get the current status of the machine. If it is free then return True, else False
        :param masch:
        :return:
        """
        freeStatus = "n"
        timecontrollPath = os.getenv('TIMECONTROLL_PATH') + rf"\{masch}work.txt"
        try:
            with open(timecontrollPath, "r") as f:
                status = f.read()
                # Check if the status is free
                if status.strip() == freeStatus:
                    return True
                else:
                    return False
        except Exception as e:
            print(f"ERROR: COULD NOT FETCH STATUS: {e}")
            return False

