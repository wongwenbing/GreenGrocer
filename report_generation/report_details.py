from datetime import date
class CustomerReport(): 
    def __init__(self, reportid, todaydate, custid, type, coverage):
        self.__custreportid = reportid
        self.__custid = custid
        self.__generated_date = todaydate
        self.__type = type
        self.__coverage = coverage
        self.__lastupdated = date.today()

    def set_reportid(self, reportid): 
        self.__custreportid = reportid
    def set_custid(self, custid): 
        self.__custid = custid
    def set_generated_date(self): 
        self.__generated_date = date.today()
    def set_type(self, type): 
        self.__type = type
    def set_coverage(self, coverage): 
        self.__coverage = coverage
    def set_lastupdated(self): 
        self.__lastupdated = date.today()

    
    def get_report_id(self): 
        return self.__custreportid
    def get_custid(self): 
        return self.__custid
    def get_generated_date(self):
        return self.__generated_date
    def get_type(self):
        return self.__type
    def get_coverage(self):
        return self.__coverage
    def get_lastupdated(self): 
        return self.__lastupdated
    
    def upload_data(self):
        return (self.__custreportid, self.__custid, self.__coverage, self.__type, self.__lastupdated)

