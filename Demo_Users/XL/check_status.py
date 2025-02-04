import time
from my_mqtt import MyMQTT


def main():
    mqtt_client = MyMQTT()

    try: 
        mqtt_client.connect()
        mqtt_client.subscribe("Channel 2 Derived Pk") # use any topic

        while True:
            time.sleep(3)

            payload = mqtt_client.get_latest_payload()
            if payload:
                print(f"Latest payload: {payload}")
            else:
                print("No new payload received.")

    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        mqtt_client.disconnect()

if __name__ == "__main__":
    main()
