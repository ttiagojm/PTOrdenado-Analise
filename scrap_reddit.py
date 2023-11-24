import requests
import re
import numpy as np
from typing import List

class ScrappingPTOrdenado:
    def __init__(self, posts):
        self.posts = posts

    def __is_portugal_city(self, cities: List[str]):
        has_pt = list()
        
        for city in cities:
            reg = re.search("\w+", city)
            if reg:
                response = requests.request("GET", f"https://www.geonames.org/search.html?q={reg.group(0)}&country=")
                countries = re.findall("/countries.*\.html", response.text)[0].strip(".html").split("/")[-1]
                has_pt.append("portuga" in countries)
            else:
                has_pt.append(False)
        return any(has_pt)
    
    def get_data(self, flair: str, field: str):
        regex_roles = re.compile(field)
        regex_age_str = re.compile(r"Idade.*")
        regex_sex = re.compile(r"\([MF]\)|\s[FM]")
        regex_xp_str = re.compile(r"Experiência profissional.*")
        regex_education = re.compile(r"Formação académica.*")
        regex_hours = re.compile(r"Horas de trabalho.*")
        regex_total = re.compile(r"Salário bruto.*")
        regex_salary = re.compile(r"Salário líquido.*")
        regex_city = re.compile(r"região de trabalho.*")

        data = {
            "Title": list(),
            "Age": list(),
            "Sex": list(),
            "Labor Hours": list(), 
            "Education": list(), 
            "Mathematics": list(),
            "Experience": list(), 
            "Portugal": list(),
            "Total Salary": list(), 
            "Salary": list()
        }
        
        for sub in self.posts:
            if sub.link_flair_text == flair and regex_roles.search(sub.title.lower()):
                # Age and Sex
                age_str = regex_age_str.search(sub.selftext)
                if age_str:
                    age = re.search(r"\d+", age_str.group(0))
                    if age:
                        age = int(age.group(0))
                    else:
                        age = np.nan
                
                    # Sex
                    sex = np.nan
                    sex_str =  regex_sex.search(age_str.group(0))
                    if sex_str:
                        sex = "M" if "M" in sex_str.group(0) else "F"
                else:
                    age = np.nan
                    sex = np.nan
                
                # years of experience
                xp_str = regex_xp_str.search(sub.selftext)
        
                if xp_str:
                    xp = re.search("\d+\.\d+|\d+\,\d+|\d+", xp_str.group(0))
                    if xp:
                        xp = float(xp.group(0).replace(",", "."))
                else:
                    xp = np.nan
                
                # Education: Bachelors or Masters degree
                edu = regex_education.search(sub.selftext)
                mat = "No"
                if edu:
                    tmp_edu = edu.group(0).lower()
                    if "licenciatura" in tmp_edu:
                        edu = "BsC"
                    elif "mestrado" in tmp_edu:
                        edu = "MsC"
                    elif "doutorado" in tmp_edu or "doutoramento" in tmp_edu or "phd" in tmp_edu:
                        edu = "PhD"
                    else:
                        edu = np.nan
        
                    # If it is a degree in math and/or statistics
                    if edu != np.nan and ("matemática" in tmp_edu or "estatística" in tmp_edu):
                        mat = "Yes"
                else:
                    edu = np.nan
        
                # Labor hours
                h = regex_hours.search(sub.selftext)
                hours = np.nan
                if h:
                    hours = re.search(r"\d+", h.group(0))
                    if hours:
                        hours = float(hours.group(0))
                    else:
                        hours = np.nan
                
                # salary and total salary per month
                total = regex_total.search(sub.selftext)
                if total:
                    total_sal = re.search("\d+", total.group(0))
                    if total_sal:
                        total_sal = float(total_sal.group(0))
                    else:
                        total_sal = np.nan
                else:
                    total_sal = np.nan
                
                sal = regex_salary.search(sub.selftext)
                salary = np.nan
                if sal:
                    salary = re.search("\d+", sal.group(0))
                    if salary:
                        salary = float(salary.group(0))
                    else:
                        salary = np.nan
        
                # Work in Portugal?
                region = regex_city.search(sub.selftext)
                if region:
                    cities = region.group(0).split(":")[1].split(" ")
                    region = "Yes" if self.__is_portugal_city(cities) else "No"
                else:
                    region = np.nan

                tmp = {
                    "Title": [sub.title,],
                    "Age": [age,],
                    "Sex": [sex,],
                    "Labor Hours": [hours,], 
                    "Education": [edu,], 
                    "Mathematics": [mat,],
                    "Experience": [xp,], 
                    "Portugal": [region,],
                    "Total Salary": [total_sal,], 
                    "Salary": [salary,]
                }
                for k,v in tmp.items():
                    data[k] += v
                    
        return data