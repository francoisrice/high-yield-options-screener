import sys
from datetime import date

# $ python daysToExpiration YYYY MM DD
if __name__ == '__main__':
    year = int(sys.argv[1])
    monthNumber = int(sys.argv[2])
    dayNumber = int(sys.argv[3])

    today = date.today()
    expiration = date(year, monthNumber, dayNumber)
    daysToExpiration = (expiration - today)
    print(daysToExpiration)
