#!/usr/bin/python
"""NFC_tag.py: Clase NFC para la interacion de los NFC tag y el sistema de registro de los alumnos"""
__author__ = "Ana María Manso Rodríguez"
__credits__ = ["Ana María Manso Rodríguez"]
__version__ = "1.0"
__status__ = "Development"

import time

import chilkat
from MFRC522 import *
import numpy as np

from db_funciones import *

# Global variable
continue_reading = False


class NFCTag:

    # Method that returns from DB the secret key
    @staticmethod
    def __get_mac_key(self):
        conecction = connect_ddbb()
        mycursor = conecction.cursor()
        mycursor.execute("SELECT sk_key FROM sk_key")
        key = mycursor.fetchone()[0]
        return key

    # Method to know NFC has been read correctly
    def is_NFC_tag(self):
        if self.data is None:
            return False
        elif len(self.data) == 48:
            return True
        else:
            return False

    # Method to read data from nfc tag
    @staticmethod
    def read_nfc(self, timeout=10):
        # Capture SIGINT for cleanup when the script is aborted
        def end_read(signal, frame):
            print("Ctrl+C captured, ending read.")
            continue_reading = False
            GPIO.cleanup()

        # Hook the SIGINT
        try:
            signal.signal(signal.SIGINT, end_read)
        except ValueError as e:
            print(e)

            # Create an object of the class MFRC522
        MIFAREReader = MFRC522()

        # Welcome message
        print("Welcome to the MFRC522 data read")
        print("Place the NFC tag in order to read it")
        timeout = time.time() + timeout
        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        while continue_reading and time.time() < timeout:

            # Scan for cards
            (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            # If a card is found
            if status == MIFAREReader.MI_OK:
                print("Card detected")

            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:

                # Print UID
                print("Card read UID: %s,%s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3], uid[4]))

                # Select the scanned tag
                MIFAREReader.MFRC522_SelectTag(uid)

                # Read all NFC data
                try:
                    for i in range(0, 45, 4):
                        a = MIFAREReader.MFRC522_Read(i)
                        if i == 0:
                            info_data = np.array(a).reshape(4, 4)
                        else:
                            info_data = np.concatenate((info_data, np.array(a).reshape(4, 4)))
                    return info_data
                except ValueError:
                    print("Reading failed, trying again")

                # If card is read correctly, exit loop
                try:
                    if (len(info_data)) == 48:
                        break
                except UnboundLocalError:
                    print("Error variable assignment, trying again")
                    print(continue_reading)

    # Authenticate NFC
    def authenticate_nfc(self):
        # Student ID read from NFC
        id_m_from_nfc = self.get_id_m()

        if id_m_from_nfc:
            # MAC key read from NFC
            mac_key = self.get_mac_from_nfc()

            # Check if MAC from NFC is authentic
            hmac_key = self.__generate_HMAC(id_m_from_nfc)

            if hmac_key == mac_key:
                return True

        else:
            return False

    # Method that returns data to write in NFC using NDEF format
    def data_to_nfc_structure(self, data0):
        data = []

        # NDEF static information
        NDEF_data = ([0x01, 0x03, 0xA0, 0x0C, 0x34, 0x03, 0x4D, 0xD1, 0x01, 0x49, 0x54, 0x02, 0x65, 0x6E])

        # Generate HMAC key for NFC autentication
        hmac_key = self.__generate_HMAC(data0)

        # Insert student ID in NFC data
        for i in list(str(data0)):
            NDEF_data.append(ord(i))
        NDEF_data.append(32)

        # Insert HMAC key in NFC data
        for i in hmac_key:
            NDEF_data.append(ord(i))
        last = hmac_key[-1]

        # NDEF data
        NDEF_data.append(0xFE)
        NDEF_data.append(0)
        NDEF_data.append(0)
        NDEF_data.append(ord(last))

        # Separate list in list of 4 elements list for NFC structure
        for i in range(22):
            data.append(NDEF_data[0 + (i * 4):4 + (i * 4)])

        return data

    # Method to clear nfc tag, sets bits to zero
    def empty_nfc(self):
        data = [0x00 for i in range(4)]

        # Capture SIGINT for cleanup when the script is aborted
        def end_read(signal, frame):
            # nonlocal continue_reading
            print("Ctrl+C captured, ending read.")
            continue_reading = False
            GPIO.cleanup()

        # Hook the SIGINT
        try:
            signal.signal(signal.SIGINT, end_read)
        except ValueError as e:
            print(e)

        # Create an object of the class MFRC522
        MIFAREReader = MFRC522()

        # Welcome message
        print("Welcome to the MFRC522 data deleting")
        print("Place the NFC tag in order to empty it")

        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        while continue_reading:

            # Scan for cards
            (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            # If a card is found
            if status == MIFAREReader.MI_OK:
                print("Card detected")

            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:

                # Print UID
                print("Card read UID: %s,%s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3], uid[4]))
                # Select the scanned tag
                MIFAREReader.MFRC522_SelectTag(uid)
                MIFAREReader.MFRC522_Read(8)

                print("Now we fill it with 0x00:")
                for i in range(36):
                    written = MIFAREReader.MFRC522_WriteUltralight(i + 4, data)

                if written:
                    print("NFC empty")
                    break;

    # Method to write data into nfc tag
    def write_nfc(self, id_m):
        continue_reading = True

        data_to_write = self.data_to_nfc_structure(id_m)

        # Capture SIGINT for cleanup when the script is aborted
        def end_read(signal, frame):
            # nonlocal continue_reading
            print("Ctrl+C captured, ending read.")
            continue_reading = False
            GPIO.cleanup()

        # Hook the SIGINT, exception for threads
        try:
            signal.signal(signal.SIGINT, end_read)
        except ValueError as e:
            print(e)

        # Create an object of the class MFRC522
        MIFAREReader = MFRC522()

        # Welcome message
        print("Welcome to the MFRC522 data read")
        print("Place the NFC tag in order to write it")

        # This loop keeps checking for chips. If one is near it will get the UID and authenticate
        while continue_reading:

            # Scan for cards
            (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

            # If a card is found
            if status == MIFAREReader.MI_OK:
                print("Card detected")

            # Get the UID of the card
            (status, uid) = MIFAREReader.MFRC522_Anticoll()

            # If we have the UID, continue
            if status == MIFAREReader.MI_OK:

                # Print UID
                print("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
                # Select the scanned tag
                MIFAREReader.MFRC522_SelectTag(uid)
                MIFAREReader.MFRC522_Read(8)
                
                written = False
                for i in range(22):
                    written = MIFAREReader.MFRC522_WriteUltralight(i + 4, data_to_write[i])

                if written:
                    print("NFC written")
                    return True
        return False

    def __init__(self):
        self.data = self.read_nfc(self)
        self.__mac_sk = self.__get_mac_key(self)

    def get_id_m(self):
        try:
            aux = []
            aux.extend(self.data[7])
            aux.extend(self.data[8])
            id_m = int("".join([chr(i) for i in aux[2:7]]))
            return id_m
        except ValueError:
            print("This NFC has no student id")
            return False
        except TypeError:
            print("No NFC has been read")
            return False

    def get_mac_from_nfc(self):
        aux = []
        for i in range(16):
            aux.extend(self.data[i + 9])
        mac = "".join([chr(i) for i in aux])
        return mac

    # Method that get NFC UID and returns it in as a num
    def get_uid_to_num(self):
        aux = []
        aux.extend(self.data[0])
        aux.extend(self.data[1])
        uid = aux[0:5]
        n = 0
        for i in range(5):
            n = n * 256 + int(uid[i])
        return n

    # Method to encrypt information
    def __generate_HMAC(self, id_m):
        crypt = chilkat.CkCrypt2()

        uid = self.get_uid_to_num()

        key_diversed = crypt.pbkdf2(self.__mac_sk, "ansi", "sha256", str(uid), 2048, 256, "hex")

        crypt.put_EncodingMode("hex")

        crypt.put_HashAlgorithm("sha256")

        crypt.SetHmacKeyEncoded(key_diversed, "ascii")

        hmac_key = crypt.hmacStringENC(str(id_m) + str(uid))

        return hmac_key
